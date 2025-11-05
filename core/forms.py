from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DonorProfile, ReceiverProfile

class UserRegistrationForm(UserCreationForm):
    """
    A form for creating new users. Includes a role selection.
    We use UserCreationForm to get the password handling.
    """
    # We add the 'role' field here, which is on our custom User model
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-md',
            'id': 'id_role'  # Important for the JavaScript in register.html
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role', 'password', 'password2') # Specify fields from User model
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'password': forms.PasswordInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
        }


class DonorProfileForm(forms.ModelForm):
    """
    Form for creating a DonorProfile.
    """
    class Meta:
        model = DonorProfile
        # These fields are now in sync with models.py
        fields = ('first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
        }


class ReceiverProfileForm(forms.ModelForm):
    """
    Form for creating a ReceiverProfile (NGO).
    """
    class Meta:
        model = ReceiverProfile
        # These fields are now in sync with models.py
        fields = ('ngo_name', 'registration_number', 'phone_number')
        widgets = {
            'ngo_name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'registration_number': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
        }

