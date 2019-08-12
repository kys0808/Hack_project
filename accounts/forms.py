
from django import forms
from django.forms import EmailField, EmailInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.db.models import EmailField
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError


from .validator import RegisteredEmailValidator


class UserRegistrationForm(UserCreationForm) :

    email = forms.EmailField(required = True)
    name = forms.CharField(required = True)

    class Meta : 

        model = get_user_model()
        fields = ('email', 'name', 'profile_image')

class VerificationEmailForm(forms.Form):

    widget = forms.EmailInput(attrs={'autofocus': True})
    email = EmailField(widget, validators=(EmailField.default_validators + [RegisteredEmailValidator()]))

class CustomUserChangeForm(forms.ModelForm) :

    error_messages = {
        'password_mismatch': "변경할 비밀번호가 일치하지 않습니다.",
    }
 
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        widget=forms.PasswordInput
        )

    password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label="New password repeated",
        strip=False,
        widget=forms.PasswordInput
        )

    class Meta:

        model = get_user_model()
        fields = ('name', 'old_password', 'password1', 'password2', 'profile_image')

    def __init__(self, *args, **kwargs):

        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):

        return self.initial["password"]

    def clean_new_password2(self):

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2