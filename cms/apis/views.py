from rest_framework import generics, viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from articles.models import Article, Comment
from articles.serializers import ArticlesSerializers, CommentSerializers, ArticlesSearchSerializer
from users.serializers import CustomUserSerializer, UserRegistrationSerializer
from django.contrib.auth import get_user_model
from django.http import Http404
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db import transaction

CustomUser = get_user_model()

#defining permission class
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit / delete it.
    Read operations are allowed for authenticated users.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.author == request.user #super().has_object_permission(request, view, obj)
    
class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow access to verified users.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated AND verified
        user = request.user
        return user.is_authenticated and getattr(user, "is_verified", False)

class ArticleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating and deleting articles.
    Lists only published articles to the public
    """
    queryset = Article.objects.all()
    serializer_class = ArticlesSerializers
    lookup_field = 'slug' #using slug to retrieve individual articles
    permission_classes = [(IsVerifiedUser | permissions.IsAuthenticatedOrReadOnly), IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Overrides the default queryset.
        -For list view (GET /articles/): SHow only published articles with publication date in the past/present
        -For detail view (GET /articles/{slug}/): SHow the specific article if its public OR if the requesting user is the author or staff
        """
        user = self.request.user
        queryset = Article.objects.all()

        if self.action == 'list':
            #Only show published articles with publication date in the past/present
            queryset = queryset.filter(is_published='published',created_at__lte = timezone.now())

        queryset = queryset.order_by("created_at")


        return queryset
    
    def perform_create(self, serializer):
        """
        Automatically set the author of the article to the requesting user
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to create an Article")
        
        serializer.save(author=self.request.user)

    def get_object(self):
        obj = super().get_object()

        if obj.is_published != 'published':
            user = self.request.user
            if not user.is_authenticated or (obj.author != user and not user.is_staff):
                raise Http404()

        return obj
    

    

# URL pattern: /articles/<slug:slug>/comments/
class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing comments of a specific article or creating a new comment for it.
    """
    serializer_class = CommentSerializers
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Authenticated users can comment

    def get_queryset(self):
        """
        Get comments for the article specified in the URL slug.
        """
        article_slug = self.kwargs.get('slug') # Get slug from URL parameters
        # Ensure the article exists and is public (or accessible to the user)
        article = get_object_or_404(
            Article,
            slug=article_slug,
            is_published='published', # Only allow comments on published articles (adjust if needed)
            created_at__lte=timezone.now()
        )
        # Return comments ordered by creation date
        return Comment.objects.filter(article=article).order_by('created_at')

    def perform_create(self, serializer):
        """
        Set the author and article for the new comment.
        """
        article_slug = self.kwargs.get('slug')
        article = get_object_or_404(
            Article,
            slug=article_slug,
            is_published='published', # Only allow commenting on published articles
            created_at__lte=timezone.now()
        )
        # Ensure user is authenticated (redundant with permission_classes but good safety)
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to comment.")

        # Save the comment, setting author and article
        serializer.save(author=self.request.user, article=article)

#articles/<slug:slug>/comments/<int:pk>/
class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific comment.
    Only the author can update or delete their comment.
    """
    queryset = Comment.objects.all() # Base queryset for comments
    serializer_class = CommentSerializers
    lookup_field = 'pk' # Default lookup field is 'pk' (ID)
    # Permissions: Authenticated users can read, author can update/delete
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

# user/create
class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    queryset = CustomUser.objects.all() # Needs a queryset though CreateAPIView doesn't query it
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register

    def perform_create(self, serializer):
        # The create method of the serializer handles user creation with password hashing
        user = serializer.save()

        #Email Verification Logic
        # 1. Generate token and expiry
        token = user.generate_verification_token() # Call the method on the user instance

        # 2. Construct the verification URL
        # Construct the full verification URL
        verification_url = self.request.build_absolute_uri(
            reverse('verify-email', kwargs={'user_id': user.pk, 'token': token})
        )

        # 3. Send the email
        subject = ("Verify your email address")
        message = f"Please click the link to verify your email: {verification_url}" # Simple plain text message

        from_email = settings.DEFAULT_FROM_EMAIL # Configured in settings.py
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
    
        except Exception as e:
            print(f"Error sending verification email: {e}")


        return user

# articles/search/?q=keyword
class ArticleSearchView(generics.ListAPIView):
    """
    API view for searching published articles by title.
    """
    serializer_class = ArticlesSerializers
    # Allow unauthenticated users to search published articles
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        """
        Filter published articles based on a search query parameter 'q'.
        """
        queryset = Article.objects.filter(
            is_published='published',
            created_at__lte=timezone.now()
        )
        query = self.request.query_params.get('q', None) # Get the 'q' query parameter

        if query:
            # Filter articles where the title contains the query keyword (case-insensitive)
            # Using Q object for potentially more complex lookups later
            queryset = queryset.filter(Q(title__icontains=query))

        # Add default ordering
        queryset = queryset.order_by('-created_at')

        return queryset
    
class ArticleSearchViewPro(generics.ListAPIView):
    """
    API view for searching published articles by mail.
    """
    serializer_class = ArticlesSearchSerializer
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        """
        Filter published articles based on a mail.
        """
        email = self.kwargs.get('email')
        User = get_object_or_404(
            get_user_model(),
            email = email
        )

        return User.articles.filter(is_published='published')
    
class EmailVerificationAPIView(APIView):
    """
    API view to handle email verification via token in URL.
    Expects user_id and token as URL parameters.
    """
    permission_classes = [permissions.AllowAny] # Anyone needs to access this to verify

    @transaction.atomic
    def get(self, request, user_id, token, format=None):
        try:
            user = CustomUser.objects.select_for_update().get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_verified:
            return Response({"detail": "Email already verified."}, status=status.HTTP_200_OK)

        if user.is_verification_token_valid(token):
            user.verify_email()
            return Response({"detail": "Email successfully verified!"}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid or expired verification token."}, status=status.HTTP_400_BAD_REQUEST)
        
            
    