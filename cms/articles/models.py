from django.db import models
from django.contrib.auth import get_user_model # Import get_user_model to get the custom user model
from django.utils.text import slugify # Import slugify helper
import os

def article_picture_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/article_pictures/<slug>/<filename>
    # Use the slug or ID to organize files for each article
    return os.path.join('article_pictures', instance.slug or str(instance.id), filename)


ARTICLE_STATUS_CHOICES = [
    ('draft', ('Draft')),
    ('published', ('Published')),
    ('archived', ('Archived')),
    ('review', ('Under Review')),
]

class Article(models.Model):
    """
    Model representing an article with fields for title, author, content,
    timestamps, slug, and an optional picture.
    """

    title = models.CharField(max_length=200, help_text="Enter the article title")

    # Add related_name for easier reverse lookups (e.g., user.articles.all())
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE, # If author is deleted, delete their articles
        related_name='articles', # Allows calling user.articles.all()
        help_text="Select the author of the article"
    )

    # Added the slug field
    # It should be unique for URLs and auto-populated
    slug = models.SlugField(
        max_length=250, # Often slightly longer than title max_length
        unique=True,    # Crucial: ensures unique URLs
        blank=True,     # Allow empty initially before saving
        null=True,      # Allow NULL in the database
        help_text="A URL-friendly slug generated from the title."
    )

    content = models.TextField(help_text="Enter the article content")

    # draft vs online
    is_published = models.CharField(
        max_length=20,
        choices=ARTICLE_STATUS_CHOICES, # Use the defined choices
        default='draft', 
        db_index=True, # Added a database index for faster filtering by status
        help_text=("The publication status of the article.")
    )

    # Use auto_now_add for creation timestamp (only set on creation)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the article was created"
    )

    # Use auto_now for last update timestamp (updated every save)
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the article was last updated"
    )

    # Added the optional picture field
    picture = models.ImageField(
        ("Article Picture"), # Optional verbose name
        upload_to=article_picture_upload_path, # Use helper for path
        blank=True, # Makes the field optional in forms/admin
        null=True,  # Allows NULL in the database
        help_text=("Optional picture for the article.") # Optional help text
    )


    class Meta:
        # Add ordering for default display (e.g., newest first)
        ordering = ['-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"


    def __str__(self):
        # A good __str__ method returning the title
        return self.title

    # Add logic to auto-populate the slug
    def save(self, *args, **kwargs):
        if not self.slug: # If slug is empty or None
            # Generate slug from the title
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Check if the slug already exists and make it unique
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug # Assign the generated unique slug

        super().save(*args, **kwargs) # Call the real save method
