from collections import ChainMap

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms import CharField, ModelForm
from django.utils.translation import gettext_lazy as _

from pythonpro.core.models import User


class NormalizeEmailMixin:
    def _normalize_email(self):
        self.data = dict(self.data.items())
        email = self.data.get('email')
        if email is not None:
            self.data['email'] = email.lower()


class UserEmailForm(ModelForm, NormalizeEmailMixin):
    current_password = CharField(label=_("Password"), strip=False, required=True)

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self._normalize_email()

    def clean(self):
        cleaned_data = super().clean()
        if not self.user.check_password(cleaned_data.get('current_password', '')):
            self.add_error('current_password', ValidationError('Senha Inválida', 'invalid_password'))
        return cleaned_data


class UserSignupForm(UserCreationForm, NormalizeEmailMixin):
    class Meta:
        model = User
        fields = ('first_name', 'email', 'source')

    def __init__(self, *args, **kwargs):
        self.plain_password = settings.DEFAULT_USER_CREATION_PASSWORD
        data = kwargs.get('data', None)
        if data is not None:
            self._set_passwords(data)
            kwargs['data'] = data
        elif args:
            query_dict = args[0]
            dct = {}
            self._set_passwords(dct)
            args = (ChainMap(query_dict, dct), *args[1:])
        super().__init__(*args, **kwargs)
        self._normalize_email()

    def _set_passwords(self, data):
        if 'password1' not in data and 'password2' not in data:
            data['password1'] = data['password2'] = self.plain_password

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


class LeadForm(UserSignupForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')

    first_name = forms.CharField(
        label=str(), widget=forms.TextInput(attrs={'placeholder': 'Qual Seu Nome?'})
    )
    email = forms.EmailField(
        label=str(), widget=forms.EmailInput(attrs={'placeholder': 'Qual seu MELHOR e-mail?'})
    )
    phone = forms.CharField(
        label=str(), widget=forms.TextInput(attrs={'placeholder': 'Qual seu número de WHATSAPP?'})
    )
    source = forms.CharField(widget=forms.HiddenInput())
    password1 = forms.CharField(widget=forms.HiddenInput())
    password2 = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.pop("autofocus", None)


class PythonProResetForm(PasswordResetForm):
    pass
    # TODO: Investigate later: https://github.com/pythonprobr/pythonpro-website/issues/4830
    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
