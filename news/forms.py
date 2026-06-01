from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class RegisterForm(UserCreationForm):
    """
    Form used to register new users with a selected role.
    """

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2',
        ]


class ArticleForm(forms.ModelForm):
    """
    Form used to create and update articles.
    """

    class Meta:
        model = Article
        fields = [
            'title',
            'content',
            'publisher',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
        }


class NewsletterForm(forms.ModelForm):
    """
    Form used to create and update newsletters.
    """

    class Meta:
        model = Newsletter
        fields = [
            'title',
            'description',
            'articles',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'articles': forms.CheckboxSelectMultiple(),
        }


class PublisherForm(forms.ModelForm):
    """
    Form used to create and update publishers.
    """

    class Meta:
        model = Publisher
        fields = '__all__'