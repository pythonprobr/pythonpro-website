from django import forms


class WaitingForm(forms.Form):
    first_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
