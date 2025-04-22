from django import forms
from django.contrib.auth.forms import UserChangeForm 
from django.core.exceptions import ValidationError # Import for validation
from .models import CustomUser # Import your custom user model


class CustomUserCreationForm(forms.ModelForm): # Inherit from forms.ModelForm
    """
    A form that creates a user, with no privileges, from an email and password.
    Uses forms.ModelForm for more control when USERNAME_FIELD is changed.
    """
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        # password and password2 are defined separately above.
        fields = ('email', 'username', 'first_name', 'last_name', 'other_name', 'occupation', 'bio', 'profile_picture')


    def clean_password2(self):
        """Validates that the two password entries match"""
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError("Passwords don't match")
        return password2 # Return the cleaned password2

    def save(self, commit=True):
        """
        Creates and saves a user using the custom manager's create_user method.
        """
        # Create the user instance but don't save to the database yet
        user = super().save(commit=False)

        # Set the password using the set_password method, which handles hashing
        user.set_password(self.cleaned_data["password"])

        # Save the user object to the database if commit is True
        if commit:
            # We call save() on the model instance, which bypasses the manager's create_user
            # unless you explicitly call user.objects.create_user(...) here.
            # The standard ModelForm save works well here after setting password.
            user.save()

            # (ModelForm handles ManyToManyField relationships after the instance is saved)
            self.save_m2m()

        return user


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating existing users. Inherits from UserChangeForm.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'other_name', 'first_name', 'last_name', 'occupation', 'bio', 'profile_picture','is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined')