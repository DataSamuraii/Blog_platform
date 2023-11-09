from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UnbanRequest


class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')


class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']


class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class UnbanRequestForm(forms.ModelForm):
    class Meta:
        model = UnbanRequest
        fields = ['content']
        labels = {
            'content': 'Please explain why you should be unbanned...',
        }
