from django import forms
from tracker.models import User, Activity


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'required': '', 'minlength': '2'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': '', 'minlength': '2'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'required': '', 'minlength': '2'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'required': '', 'minlength': '2'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'required': '', 'class': 'required email'}))

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')


class ActivityForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'required': '', 'minlength': '2'}))

    class Meta:
        model = Activity

