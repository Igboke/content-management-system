from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Article, Comment
from .serializers import ArticlesSerializers, ArticlesSearchSerializer, CommentSerializers

# Get your custom user model
CustomUser = get_user_model()
