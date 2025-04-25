from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.utils import timezone
import os
from django.contrib.auth.tokens import default_token_generator
import uuid


class CustomUserManager(BaseUserManager): # Inherit from BaseUserManager
    """
    Custom user manager where email is the unique identifier (USERNAME_FIELD).
    Provides methods to create users and superusers.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given email and password.
        Additional fields can be passed via extra_fields.
        """
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email) # Normalize the email address

        # Get the User model dynamically. Required in managers.
        UserModel = get_user_model()

        # Create the user instance.
        # Note: AbstractUser still has a 'username' field.
        # Since REQUIRED_FIELDS is empty, createsuperuser won't prompt for it,
        # The AbstractUser base class handles defaults for fields like is_active, etc.
        user = UserModel(email=email, **extra_fields) # Set email directly

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        Sets necessary staff and superuser flags.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    # Add any additional fields you want to include in the custom user model
    other_name = models.CharField(max_length=150, blank=True, null=True, help_text="Optional other name")
    email = models.EmailField(unique=True, help_text="Required. Enter a valid email address.")
    bio = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_verified = models.BooleanField(
        ("verified"),
        default=False,
        help_text=("Designates whether the user has verified their email address.")
    )
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_token_expires = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def generate_verification_token(self):
        #generate a UUID token
        token = str(uuid.uuid4())
        expiry_time = timezone.now() + timezone.timedelta(days=1)

        self.email_verification_token = token
        self.email_verification_token_expires = expiry_time
        self.save()

        return token
    
    def is_verification_token_valid(self, token):
        # Check if a token exists, matches the provided token, and is not expired
        #using UUID token:
        return (self.email_verification_token is not None and
                self.email_verification_token == token and
                self.email_verification_token_expires is not None and
                self.email_verification_token_expires > timezone.now())

    # Optional: Method to mark user as verified
    def verify_email(self):
        self.is_verified = True
        self.email_verification_token = None # Clear the token after use
        self.email_verification_token_expires = None
        self.save()

    class Meta:
        verbose_name = ("user")
        verbose_name_plural = ("users")

    def __str__(self):
        return self.email
