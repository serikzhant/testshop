from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput

User = get_user_model()


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserCreateForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = "Your Email Address"
        self.fields['email'].required = True
        self.fields['username'].help_text = None
        self.fields['password2'].help_text = None

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        username = self.cleaned_data['username'].lower()

        if User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'Email addresses must be unique.')

        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = "Your Email Address"
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ('password1', 'password2')
