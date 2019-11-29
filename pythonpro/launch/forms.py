from django import forms


class LeadForm(forms.Form):
    email = forms.EmailField(required=True)
