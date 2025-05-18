"""
Forms for the users app.

This module contains forms for user registration, profile management,
and other user-related functionality.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    """
    Extended user registration form with email field and role selection.
    
    This form extends Django's UserCreationForm to include an email field,
    role selection (student/instructor), and customize the styling/validation 
    with simplified password requirements.
    """
    email = forms.EmailField()
    ROLE_CHOICES = (
        (False, 'Student'),
        (True, 'Instructor')
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.RadioSelect(),
        initial=False,
        help_text='Select your role in the academic platform'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field_name].label
            })
        
        # Simplify password requirements
        self.fields['password1'].help_text = 'Create a password you can remember.'
        
        # Remove some of the default password validators messages
        self.fields['password1'].validators = []


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with remember me field.
    """
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    
    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            if field_name != 'remember_me':
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[field_name].label
                })


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information.
    
    This form allows users to update their username and email.
    """
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    
    This form allows users to update their profile information including 
    avatar, bio, contact details, etc.
    """
    class Meta:
        model = Profile
        fields = [
            'avatar', 'bio', 'date_of_birth', 'phone_number',
            'website', 'address', 'social_linkedin', 'social_twitter',
            'social_github', 'email_notifications'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'email_notifications': forms.CheckboxInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            if field_name != 'email_notifications':
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control'
                })
            else:
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-check-input'
                })
        
        # Make certain fields optional
        optional_fields = [
            'avatar', 'bio', 'date_of_birth', 'phone_number',
            'website', 'address', 'social_linkedin', 'social_twitter', 'social_github'
        ]
        for field in optional_fields:
            self.fields[field].required = False


class EnrollmentForm(forms.Form):
    """
    Form for enrolling in a course.
    
    This simple form is used when a user wants to enroll in a course.
    It may include additional fields like a confirmation checkbox or
    payment information depending on the course requirements.
    """
    confirm = forms.BooleanField(
        required=True,
        label='I confirm that I want to enroll in this course',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
