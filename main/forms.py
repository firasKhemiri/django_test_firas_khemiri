from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from main.models import Order


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required.')
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = ('username', 'is_superuser', 'email', 'password',)


class OrderForm(forms.ModelForm):
    object = forms.CharField(max_length=254, help_text='Required.')
    price = forms.FloatField(help_text='Required.')

    class Meta:
        model = Order
        fields = ('object', 'price', 'user')
