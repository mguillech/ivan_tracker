from django import forms
from tracker.models import User, Activity, Category


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
    category = forms.CharField(widget=forms.Select(attrs={'required': ''}))

    class Meta:
        model = Activity
        exclude = ('rating',)

    def clean_category(self):
        category_id = self.cleaned_data['category']
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise forms.ValidationError('The category does not exist')
        else:
            return category


class CategoryForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'required': '', 'minlength': '2'}))

    class Meta:
        model = Category

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            _ = Category.objects.get(name=name)
        except Category.DoesNotExist:
            return name
        else:
            raise forms.ValidationError('Such a category already exists')
