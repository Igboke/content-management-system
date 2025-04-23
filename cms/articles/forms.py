from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    """
    Form for creating and updating Article instances.
    """
    class Meta:
        model = Article
        fields = ['title', 'author', 'content', 'picture','is_published']  # Include all fields except slug
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8, 'cols': 40}),  # Customize the content field
        }