from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Article, Comment
from .serializers import ArticlesSerializers, ArticlesSearchSerializer, CommentSerializers
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, ScopedRateThrottle


# Get your custom user model
CustomUser = get_user_model()

class ArticleTests(APITestCase):
    """
    Test for model and related API views
    """
    def setUp(self):
        """
        Set up test data that will be used across multiple tests in this class.
        setUp runs before each test method (each method starting with test_).
        """
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password13456"
        )
        self.staff_user = CustomUser.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="staffuserpassword",
            is_staff = True
        )
        self.article_draft = Article.objects.create(
            title = "This is a draft article",
            author = self.user,
            content = "Draft Article",
            is_published = "draft"
        )
        self.article_published = Article.objects.create(
            title= "Published Article",
            author = self.user,
            content = "This is the published Article",
            is_published = "published"
        )

        self.article_list_create_url = reverse('article-list-create') # Or your router's list name
        self.article_detail_url = lambda slug: reverse('article-detail-update-delete', kwargs={'slug': slug})

    # Test Cases for Article Model Methods
    def test_article_is_public_property(self):
        """Test the is_public property on the Article model."""
        self.assertTrue(self.article_published.is_published_)
        self.assertFalse(self.article_draft.is_published_)

    # Test Cases for Article List API View (GET /articles/)
    def test_list_articles_unauthenticated(self):
        """Anyone should be able to list public articles."""
        response = self.client.get(self.article_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that only published articles are returned
        self.assertEqual(len(response.data), 1) # Only article_public should be returned
        self.assertEqual(response.data[0]['title'], self.article_published.title)

    def test_list_articles_authenticated(self):
        """Authenticated users should also only see public articles in the list."""
        self.client.force_authenticate(user=self.user) # Authenticate the client
        response = self.client.get(self.article_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.article_published.title)
        self.client.force_authenticate(user=None) # Log out the client after the test

    # --- Test Cases for Article Create API View (POST /articles/) ---
    def test_create_article_authenticated(self):
        """Authenticated users should be able to create articles."""
        self.client.force_authenticate(user=self.user)
        initial_article_count = Article.objects.count()
        new_article_data = {
            'title': 'New Article from Test',
            'content': 'Content for the new article.',
            # Do not provide author, status, publication_date, slug - server should set
        }
        response = self.client.post(self.article_list_create_url, new_article_data, format='json') # format='json' sets Content-Type

        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # 201 Created status
        self.assertEqual(Article.objects.count(), initial_article_count + 1) # Check if article was created
        created_article = Article.objects.latest('created_at') # Get the latest created article
        self.assertEqual(created_article.title, new_article_data['title'])
        self.assertEqual(created_article.author, self.user) # Check if author was set correctly
        self.assertEqual(created_article.is_published, 'draft') # Check default status

        self.client.force_authenticate(user=None)
    
    def test_create_article_unauthenticated(self):
        """Unauthenticated users should NOT be able to create articles (due to IsAuthenticatedOrReadOnly)."""
        initial_article_count = Article.objects.count()
        new_article_data = {'title': 'Should Not Create', 'content': 'nada',}
        response = self.client.post(self.article_list_create_url, new_article_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # 401 Unauthorized
        self.assertEqual(Article.objects.count(), initial_article_count) # Ensure no article was created

    # Test Cases for Article Detail API View (GET /articles/{slug}/)
    def test_retrieve_public_article_unauthenticated(self):
        """Anyone should be able to retrieve a public article by slug."""
        url = self.article_detail_url(self.article_published.slug)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article_published.title)

    def test_retrieve_draft_article_unauthenticated(self):
        """Unauthenticated users should NOT be able to retrieve a draft article."""
        url = self.article_detail_url(self.article_draft.slug)
        response = self.client.get(url)
        # This should return 404 because the object is filtered out for unauthenticated users in the ViewSet's get_queryset, or 403 if caught by permission
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Or HTTP_403_FORBIDDEN

    # --- Test Cases for Article Update API View (PATCH /articles/{slug}/) ---
    def test_update_article_as_author(self):
        """Author should be able to update their own article."""
        self.client.force_authenticate(user=self.user) # Authenticate as the author
        url = self.article_detail_url(self.article_published.slug)
        updated_data = {'content': 'Updated content from author.'}
        response = self.client.patch(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK) # 200 OK
        self.article_published.refresh_from_db() # Reload the article from the database
        self.assertEqual(self.article_published.content, updated_data['content'])
        self.client.force_authenticate(user=None)
    
    def test_update_article_as_different_user(self):
        """Different authenticated user should NOT be able to update another user's article."""
        other_user = CustomUser.objects.create_user(username='other', email='other@ex.com', password='pass')
        self.client.force_authenticate(user=other_user) # Authenticate as a different user
        url = self.article_detail_url(self.article_published.slug)
        updated_data = {'content': 'Attempted update.'}
        response = self.client.patch(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # 403 Forbidden
        self.client.force_authenticate(user=None)
    
    def test_update_article_unauthenticated(self):
        """Unauthenticated user should NOT be able to update an article."""
        url = self.article_detail_url(self.article_published.slug)
        updated_data = {'content': 'Attempted update.'}
        response = self.client.patch(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # 401 Unauthorized

class CommentTests(APITestCase):
    """Tests for the Comment API views."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='u1', 
                                                   email='u1@ex.com', 
                                                   password='pass')
        self.article_public = Article.objects.create(
            title='Commentable Article',
            author=self.user,
            content='Hello from the other side',
            is_published='published',
        )
        self.comment_list_create_url = lambda slug: reverse('comment-list-create', kwargs={'slug': slug})
        self.comment_detail_url = lambda pk,slug: reverse('comment-detail-update-delete', kwargs={'pk': pk,'slug':slug})
    
    def test_list_comments_for_article(self):
        """Anyone should be able to list comments for a public article."""
        Comment.objects.create(article=self.article_public, author=self.user, content='First comment!')
        Comment.objects.create(article=self.article_public, author=self.user, content='Second comment!')

        url = self.comment_list_create_url(self.article_public.slug)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], 'First comment!') # Check ordering

    def test_create_comment_authenticated(self):
        """Authenticated users should be able to create comments on a public article."""
        self.client.force_authenticate(user=self.user)
        initial_comment_count = Comment.objects.count()
        url = self.comment_list_create_url(self.article_public.slug)
        comment_data = {'content': 'This is a new comment!'}

        response = self.client.post(url, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), initial_comment_count + 1)
        created_comment = Comment.objects.latest('created_at')
        self.assertEqual(created_comment.content, comment_data['content'])
        self.assertEqual(created_comment.author, self.user)
        self.assertEqual(created_comment.article, self.article_public)

        self.client.force_authenticate(user=None)

    def test_create_comment_unauthenticated(self):
        """Unauthenticated users should NOT be able to create comments."""
        initial_comment_count = Comment.objects.count()
        url = self.comment_list_create_url(self.article_public.slug)
        comment_data = {'content': 'Should not work!'}

        response = self.client.post(url, comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), initial_comment_count)

class ArticleSearchTests(APITestCase):
     def setUp(self):
         # Create articles with different titles and authors
         self.user1 = CustomUser.objects.create_user(username='u1', 
                                                     email='u1@ex.com',
                                                     password='pass'
                                                     )
         self.user2 = CustomUser.objects.create_user(username='u2', 
                                                     email='u2@ex.com', 
                                                     password='pass'
                                                     )
         self.article1 = Article.objects.create(title='Django Tutorial', 
                                                author=self.user1, 
                                                is_published='published'
                                                )
         self.article2 = Article.objects.create(title='Python Basics', 
                                                author=self.user2, 
                                                is_published='published'
                                                )
         self.article3 = Article.objects.create(title='More Django', 
                                                author=self.user1, 
                                                is_published='draft'
                                                ) # Draft

         self.search_url_title = reverse('article-search') 
         self.search_url_email = reverse('article-search-email', kwargs={'email': 'u1@ex.com'}) 

     def test_search_by_title(self):
         response = self.client.get(self.search_url_title, {'q': 'Django'}) # Pass query param
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(len(response.data), 1) # Only public articles matching "Django"
         self.assertEqual(response.data[0]['title'], self.article1.title)

     def test_search_by_author_email(self):
        #  url = reverse('article-search-email', kwargs={'email': 'u1@ex.com'}) # Pass email param
         response = self.client.get(self.search_url_email) 
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(len(response.data), 1) # Only public articles by user1
         self.assertEqual(response.data[0]['title'], self.article1.title)

     def test_search_no_results(self):
         response = self.client.get(self.search_url_title, {'q': 'NonExistent'})
         self.assertEqual(response.status_code, status.HTTP_200_OK)
         self.assertEqual(len(response.data), 0) # Expect empty list

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("create-user")
        self.user_profile = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "string",
            "password2": "string",
            "first_name": "string",
            "last_name": "string",
            "other_name": "string",
            "occupation": "occupation",
            "bio": "bio of the user created from test",
            # "profile_picture": "string"
        }
        self.test_token_creation_url = reverse("obtain-token")
    
    def test_register_new_user(self):
        token_data = {
                "username": self.user_profile['email'],
                "password": self.user_profile['password']
            }
        register_response = self.client.post(
            self.register_url,
            self.user_profile,
            format='json'
        )
        token_response = self.client.post(
            self.test_token_creation_url,
            token_data,
            format='json'
        )
        self.assertEqual(register_response.status_code,status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email=self.user_profile['email']).exists())
        # Check if the user is created
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in token_response.data) # Check if the token is returned in the response

    def test_verify_new_user(self):
        # create user via create_user to ensure password hashing and logic
        user = CustomUser.objects.create_user(
            username="tragic",
            email="test@user.com",
            password="testpass123"
        )

        # generate a verification token
        token = user.generate_verification_token()

        self.assertFalse(user.is_verified)
        self.assertTrue(len(token) > 1)

        # build verification URL
        url = reverse('verify-email', kwargs={'user_id': user.pk, 'token': token})
        response = self.client.get(url)

        # test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Email successfully verified!")

        # refresh from DB to check if marked verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)


class ThrottleTests(APITestCase):
    """
    Tests for API rate limiting.
    """
    def setUp(self):
        """Set up a user for authenticated tests."""
        self.user = CustomUser.objects.create_user(
            username='throttleuser',
            email='throttle@example.com',
            password='throttlepassword'
        )

        # Get URLs
        self.article_list_create_url = reverse('article-list-create')
        self.obtain_token_url = reverse('obtain-token')
        self.comment_list_create_url = lambda slug: reverse('comment-list-create', kwargs={'slug': slug})

        self.article_commentable = Article.objects.create(
            title='Comment Test Article',
            author=self.user,
            content='to be or not to be',
            is_published='published',
        )
    
    def test_registration_rate_limit_anonymous(self):
        """Anonymous users should be rate-limited on registration endpoint."""
        # We'll simulate hitting a '5/minute' limit
        registration_url = reverse('create-user')
        test_limit = 5
        test_email_base = 'testanon{}@example.com'
        test_password = 'password'

        print(f"\n--- Testing anonymous registration rate limit ({test_limit}/minute) ---")

        for i in range(test_limit):
            user_data = {
            "username": f'anonuser{i}',
            "email":  test_email_base.format(i),
            "password": test_password,
            "password2": test_password,
            "first_name": "string",
            "last_name": "string",
            "other_name": "string",
            "occupation": "occupation",
            "bio": "bio of the user created from test",
            # "profile_picture": "string"
        }
            response = self.client.post(registration_url, user_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Request {i+1} failed unexpectedly with status {response.status_code}")

        # The next request should be rate limited
        print(f"--- Sending {test_limit + 1}th request ---")
        user_data= {
            "username": f'anonuser{test_limit}',
            "email":  test_email_base.format(test_limit),
            "password": test_password,
            "password2": test_password,
            "first_name": "string",
            "last_name": "string",
            "other_name": "string",
            "occupation": "occupation",
            "bio": "bio of the user created from test",
            # "profile_picture": "string"
        }
        response = self.client.post(registration_url, user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS) # Expect 429
        self.assertIn('Retry-After', response.headers) # Check for Retry-After header
        print(f"Successfully received 429 with Retry-After: {response.headers.get('Retry-After')}")

    def test_user_rate_limit_authenticated(self):
        """Authenticated users should be rate-limited on a throttled endpoint."""
        # Let's simulate hitting a '50/day' limit for the authenticated user
        test_limit = 50
        url_to_test = self.article_list_create_url

        self.client.force_authenticate(user=self.user) # Authenticate

        print(f"\n--- Testing authenticated user rate limit ({test_limit}/day) ---")

        for i in range(test_limit):
            response = self.client.get(url_to_test)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Request {i+1} failed unexpectedly with status {response.status_code}")

        # The next request should be rate limited
        print(f"--- Sending {test_limit + 1}th request ---")
        response = self.client.get(url_to_test)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response.headers)
        print(f"Successfully received 429 with Retry-After: {response.headers.get('Retry-After')}")

        self.client.force_authenticate(user=None) # Log out

    def test_comment_create_rate_limit_authenticated(self):
        """Authenticated users should be rate-limited on comment creation."""
        test_limit = 15
        url_to_test = self.comment_list_create_url(self.article_commentable.slug)
        comment_data = {'content': 'Test comment {}'}

        self.client.force_authenticate(user=self.user)

        print(f"\n--- Testing authenticated comment creation rate limit ({test_limit}/hour) ---")

        for i in range(test_limit):
            data = {'content': comment_data['content'].format(i+1)}
            response = self.client.post(url_to_test, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Request {i+1} failed unexpectedly with status {response.status_code}")

        # The next request should be rate limited
        print(f"--- Sending {test_limit + 1}th request ---")
        data = {'content': comment_data['content'].format(test_limit + 1)}
        response = self.client.post(url_to_test, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response.headers)
        print(f"Successfully received 429 with Retry-After: {response.headers.get('Retry-After')}")

        self.client.force_authenticate(user=None)

    #Adding more tests for other endpoints with specific throttles (Search, Login)
    def test_search_rate_limit(self):
        """Authenticated users should be rate-limited on search."""
        test_limit = 6
        url_to_test = reverse('article-search')
        search_data = {'q': 'Django'}

        self.client.force_authenticate(user=self.user)

        print(f"\n--- Testing authenticated search rate limit ({test_limit}/minute) ---")

        for i in range(test_limit):
            response = self.client.get(url_to_test, search_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Request {i+1} failed unexpectedly with status {response.status_code}")

        # The next request should be rate limited
        print(f"--- Sending {test_limit + 1}th request ---")
        response = self.client.get(url_to_test, search_data)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response.headers)
        print(f"Successfully received 429 with Retry-After: {response.headers.get('Retry-After')}")
        self.client.force_authenticate(user=None) # Log out

        print(f"\n--- Testing inauthenticated search rate limit ({test_limit}/minute) ---")
        for i in range(test_limit):
            response = self.client.get(url_to_test, search_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"Request {i+1} failed unexpectedly with status {response.status_code}")
        # The next request should be rate limited
        print(f"--- Sending {test_limit + 1}th request ---")
        response = self.client.get(url_to_test, search_data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response.headers)
        print(f"Successfully received 429 with Retry-After: {response.headers.get('Retry-After')}")

# Test the ThrottledObtainAuthToken view
class AuthThrottleTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='loginuser', 
                                                   email='login@ex.com', 
                                                   password='loginpass')
        self.obtain_token_url = reverse('obtain-token')

    def test_login_rate_limit_anonymous(self):
        """Anonymous users should be rate-limited on the login endpoint."""
    
        test_limit = 5
        login_data = {'username': 'login@ex.com', 'password': 'loginpass'}

        print(f"\n--- Testing anonymous login rate limit ({test_limit}/minute) ---")

        for i in range(test_limit):
            response = self.client.post(self.obtain_token_url, login_data, format='json')

        # The next request should be rate limited
        print(f"--- Sending {test_limit + 1}th request ---")
        response = self.client.post(self.obtain_token_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response.headers)
        print(f"Successfully received 429 with Retry-After: {response.headers.get('Retry-After')}")

class LoginTests(APITestCase):
    """
    Tests for the login functionality.
    """
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='loginuser',
                                           email='loginuser@test.com',
                                           password='loginpassword')
        self.login_url = reverse('login')
        self.login_data = {
            'email': self.user.email,
            'password': 'loginpassword'
        }
    def test_login_api(self):
        """Test the login API with valid credentials."""
        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Login successful.')
    
    def test_login_api_invalid_credentials(self):
        """Test the login API with invalid credentials."""
        response = self.client.post(self.login_url,{'email':'fakemail@gmail.com','password':'wrongpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
        
        
        

    

    
    

        