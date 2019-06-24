from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm
from django.utils.translation import gettext_lazy as _

from pythonpro.core.models import User


class UserEmailForm(ModelForm):
    current_password = CharField(label=_("Password"), strip=False, required=True)

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.user.check_password(cleaned_data.get('current_password', '')):
            self.add_error('current_password', ValidationError('Senha Inválida', 'invalid_password'))
        return cleaned_data


class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        required=False,
        widget=forms.PasswordInput,

    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        required=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def save(self, commit=True, source=None):
        user = super().save(commit=False)
        user.set_password(User.objects.make_random_password(30))
        user.source = source
        if commit:
            user.save()
        return user
