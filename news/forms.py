from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


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