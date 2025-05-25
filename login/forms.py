from django import forms

class FyersLoginForm(forms.Form):
    client_id = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Client ID',
        'class': 'form-control',
    }))
    secret_key = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={
        'placeholder': 'Secret Key',
        'class': 'form-control',
    }))
