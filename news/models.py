from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model for the news application.

    Roles:
    - Reader: can view articles and newsletters.
    - Editor: can review, approve, update, and delete content.
    - Journalist: can create, update, and delete own content.
    """

    READER = 'reader'
    EDITOR = 'editor'
    JOURNALIST = 'journalist'

    ROLE_CHOICES = [
        (READER, 'Reader'),
        (EDITOR, 'Editor'),
        (JOURNALIST, 'Journalist'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER
    )

    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='subscribers'
    )

    subscribed_journalists = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='subscribers_to_journalist'
    )

    def __str__(self):
        return f'{self.username} ({self.role})'


class Publisher(models.Model):
    """
    Represents a publication that can have editors and journalists.
    """

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='editor_publishers',
        limit_choices_to={'role': CustomUser.EDITOR}
    )

    journalists = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='journalist_publishers',
        limit_choices_to={'role': CustomUser.JOURNALIST}
    )

    def __str__(self):
        return self.name


class Article(models.Model):

    """Represents a news article submitted and managed by users."""

    title = models.CharField(max_length=255)
    content = models.TextField()

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='articles',
        limit_choices_to={'role': CustomUser.JOURNALIST}
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Represents a curated collection of articles.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='newsletters',
        limit_choices_to={'role': CustomUser.JOURNALIST}
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name='newsletters'
    )

    def __str__(self):
        return self.title


class ApprovedArticleLog(models.Model):
    """
    Stores records of approved articles posted to the internal API.
    """

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='approval_logs'
    )

    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Approval log for {self.article.title}'
