from django.contrib import admin
from .models import Article, Comment
from .forms import ArticleForm

class CommentInline(admin.TabularInline):
    """
    Inline admin for comments related to an article.
    Allows adding/editing comments directly in the article admin.
    """
    model = Comment
    extra = 1  # Number of empty forms to display for adding new comments

class ArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Article model.
    Uses custom form and adjusts field display.
    """
    inlines = [CommentInline]  # Include comments inline in the article admin
    form = ArticleForm  # Use the custom form defined in forms.py
    list_display = ('title', 'author', 'created_at', 'updated_at')  # Fields to display in the list view
    search_fields = ('title', 'author__email')  # Fields to use for searching
    list_filter = ('is_published','created_at', 'updated_at')  # Fields to use for filtering in the sidebar
    prepopulated_fields = {'slug': ('title',)}  # Automatically populate slug from title

    # Optional: Customize the form layout in the admin interface
    fieldsets = (
        (None, {'fields': ('title', 'author', 'slug', 'content', 'picture','is_published')}),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Comment model.
    Uses custom form and adjusts field display.
    """
    list_display = ('article', 'author', 'created_at', 'updated_at')  # Fields to display in the list view
    search_fields = ('article__title', 'author__email')  # Fields to use for searching
    list_filter = ('created_at', 'updated_at','status')  # Fields to use for filtering in the sidebar

admin.site.register(Article, ArticleAdmin)
