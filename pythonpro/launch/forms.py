from django import forms
from django.forms.utils import ErrorList


class LeadForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)
        self._normalize_email()

    def _normalize_email(self):
        self.data = dict(self.data.items())
        email = self.data.get('email')
        if email is not None:
            self.data['email'] = email.lower()
