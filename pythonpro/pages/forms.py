from django import forms


class NameEmailForm(forms.Form):
    name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Insira seu Nome'}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'Insira seu Email'}))


class NameEmailPhoneForm(NameEmailForm):
    phone = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Insira seu WhatsApp (não se esqueça do DDD)'})
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone = phone.replace('(', '')
        phone = phone.replace(')', '')
        phone = phone.replace(' ', '')
        phone = phone.replace('-', '')
        return phone
