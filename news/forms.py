from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class RegisterForm(UserCreationForm):
    """
    Form used to register new users with a selected role.

    The email field is checked manually so users get a clear error message
    instead of the database crashing when a duplicate email is submitted.
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

    def clean_email(self):
        """
        Prevent duplicate email addresses during registration.
        """
        email = self.cleaned_data.get('email')

        if email:
            email = email.strip().lower()

            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    'An account with this email address already exists.'
                )

        return email


class ArticleForm(forms.ModelForm):
    """
    Form used by journalists and editors to create or update articles.
    """

    class Meta:
        model = Article
        fields = [
            'title',
            'content',
            'publisher',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter article title',
                }
            ),
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'placeholder': 'Write the article content here',
                }
            ),
            'publisher': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
        }


class NewsletterForm(forms.ModelForm):
    """
    Form used by journalists and editors to create or update newsletters.
    """

    class Meta:
        model = Newsletter
        fields = [
            'title',
            'description',
            'articles',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter newsletter title',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Enter newsletter description',
                }
            ),
            'articles': forms.CheckboxSelectMultiple(),
        }


class PublisherForm(forms.ModelForm):
    """
    Form used by editors to create or update publishers.
    """

    class Meta:
        model = Publisher
        fields = [
            'name',
            'description',
            'editors',
            'journalists',
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter publisher name',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Enter publisher description',
                }
            ),
            'editors': forms.CheckboxSelectMultiple(),
            'journalists': forms.CheckboxSelectMultiple(),
        }


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