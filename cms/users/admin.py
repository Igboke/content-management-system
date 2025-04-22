from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the CustomUser model.
    Uses custom forms and adjusts field display.
    """
    # Specify the custom forms to use for adding (add_form) and changing users(form)
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # List of fields to display in the list view
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')

    # Fields to use for searching
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Fields to use for filtering in the sidebar
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    # How fields are grouped and ordered in the change form
    # overrides the default UserAdmin fieldsets to include your custom fields
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # Base authentication info
        ('Personal info', {'fields': ('first_name', 'last_name', 'other_name', 'username', 'occupation', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # How fields are grouped and ordered in the add form
    # This is separate from fieldsets and specifically for the "Add User" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # Optional: make the section wide
            'fields': ('email', 'username', 'other_name', 'first_name', 'last_name', 'occupation', 'bio', 'profile_picture', 'password', 'password2'),
            # password and password2 (confirmation) are handled by UserCreationForm automatically
        }),
    )

    # this handles ManyToManyFields like 'groups' and 'user_permissions'
    # It uses a nice interface with two horizontal select boxes
    filter_horizontal = ('groups', 'user_permissions',)

    




admin.site.register(CustomUser, CustomUserAdmin)
