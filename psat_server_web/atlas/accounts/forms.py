"""
Forms for user account management.
"""
from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


class CreateUserForm(forms.Form):
    """
    Form for creating new users with profile settings.
    Only accessible by admin users.
    """
    # User basic information
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        }),
        help_text='Required. Letters, digits and @/./+/-/_ only.'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        }),
        help_text='Required. Valid email address.'
    )
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        }),
        help_text='Required. First name of the user.'
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        }),
        help_text='Required. Last name of the user.'
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        }),
        help_text='Optional. Upload a profile image (.gif, .png, .jpg).'
    )
    
    # Group selection for token expiration and write access
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a group",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text=(
            'Select group to determine API token expiration time and '
            'write access permissions.'
        )
    )
    
    def clean_username(self):
        """Validate that username is unique."""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_email(self):
        """Validate that email is unique."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email