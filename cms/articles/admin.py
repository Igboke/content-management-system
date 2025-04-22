from django.contrib import admin
from .models import Article
from .forms import ArticleForm

class ArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Article model.
    Uses custom form and adjusts field display.
    """
    form = ArticleForm  # Use the custom form defined in forms.py
    list_display = ('title', 'author', 'created_at', 'updated_at')  # Fields to display in the list view
    search_fields = ('title', 'author__email')  # Fields to use for searching
    list_filter = ('created_at', 'updated_at')  # Fields to use for filtering in the sidebar
    prepopulated_fields = {'slug': ('title',)}  # Automatically populate slug from title

    # Optional: Customize the form layout in the admin interface
    fieldsets = (
        (None, {'fields': ('title', 'author', 'slug', 'content', 'picture')}),
    )

admin.site.register(Article, ArticleAdmin)
