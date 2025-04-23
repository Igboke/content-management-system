from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth import get_user_model
from users.serializers import CustomUserSerializer


class CommentSerializers(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only = True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'updated_at')

        # Define fields that should be read-only
        read_only_fields = ('id', 'article', 'author', 'created_at', 'updated_at')
        pass

class ArticlesSerializers(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only = True)
    comment = CommentSerializers(many=True,read_only=True)

    class Meta:
        model = Article

        # Define fields for output (GET requests)
        fields = ('id', 'title', 'slug', 'author', 'content', 'created_at', 'updated_at', 'picture', 'is_published','comment')

        # Define fields that should be read-only (included in output, ignored on input)
        read_only_fields = ('id', 'slug', 'author', 'created_at', 'updated_at')
