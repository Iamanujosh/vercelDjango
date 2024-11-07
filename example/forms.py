from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from django import forms
from .models import WardrobeItem
from .models import UserInfo

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = [
            'photo', 'body_type', 'skin_tone', 'height', 'weight', 
            'location', 'age_group', 'gender', 'types_of_clothes', 'sleeves'
        ]

        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'body_type': forms.Select(attrs={'class': 'form-select'}),
            'skin_tone': forms.Select(attrs={'class': 'form-select'}),
            'age_group': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'types_of_clothes': forms.Select(attrs={'class': 'form-select'}),
            'sleeves': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your location'}),
        }


class WardrobeItemForm(forms.ModelForm):
    class Meta:
        model = WardrobeItem
        fields = ['name', 'image', 'category', 'last_worn', 'color', 'fav']
        widgets = {
            'last_worn': forms.DateInput(attrs={'type': 'date'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    username = forms.CharField(max_length=150, 
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Username'
                               }),
                               help_text="")  # Blank out the help text

    password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # Override the clean_username method to explicitly validate the username conditions
    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Username can only contain letters, digits and @/./+/-/_ characters.")
        return username