import json

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import UnbanRequest, EmailSubscriber


class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['profile_picture', 'username', 'bio', 'email', 'first_name', 'last_name', 'social_media']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'social_media': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter JSON format'}),
        }

    def clean_social_media(self):
        social_media = self.cleaned_data.get('social_media')
        if not social_media:
            return {}

        return social_media


class EmailSubscriberForm(forms.ModelForm):
    class Meta:
        model = EmailSubscriber
        fields = []


class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class UnbanRequestForm(forms.ModelForm):
    class Meta:
        model = UnbanRequest
        fields = ['content']
        labels = {
            'content': 'Please explain why you should be unbanned...',
        }
