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
        fields = ('first_name', 'email', 'source')

    def __init__(self, *args, **kwargs):
        self.plain_password = User.objects.make_random_password(30)
        data = kwargs.get('data', None)
        if data is not None:
            self._set_passwords(data)
            kwargs['data'] = data
        elif args:
            self._set_passwords(args[0])
        super().__init__(*args, **kwargs)

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
