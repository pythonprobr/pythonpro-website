from django import forms


class WaitingForm(forms.Form):
    first_name = forms.CharField(
        label="", widget=forms.TextInput(attrs={'placeholder': 'Digite seu nome'})
    )
    email = forms.EmailField(
        label="", widget=forms.EmailInput(attrs={'placeholder': 'Digite seu MELHOR email'})
    )
    phone = forms.CharField(
        label="", widget=forms.TextInput(attrs={'placeholder': 'Digite seu WhatsApp (não se esqueça do DDD)'})
    )
