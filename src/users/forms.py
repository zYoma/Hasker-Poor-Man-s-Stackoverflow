import re
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Login')
    email = forms.EmailField(max_length=200)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)
    avatar = forms.ImageField()
    error_css_class = 'error'

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'avatar')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Данный email уже есть в БД!')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not re.match(r'^[a-zA-Z0-9_-]{3,16}$', username):
            raise ValidationError('Недопустимые символы в логине!')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Данный логин уже кем-то используется!')

        return username

    def clean_password2(self):
        password2 = self.cleaned_data['password2'].strip()
        password = self.cleaned_data['password'].strip()
        if password2 != password:
            raise ValidationError('Введенные пароли не совпадают!')
        return password2


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'avatar')
