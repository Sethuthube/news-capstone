from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model for the news application.

    Roles:
    - Reader: can view articles and newsletters.
    - Editor: can review, approve, update, and delete content.
    - Journalist: can create, update, and delete own content.

    The user's Django group is automatically synced to match their role.
    """

    READER = 'reader'
    EDITOR = 'editor'
    JOURNALIST = 'journalist'

    ROLE_CHOICES = [
        (READER, 'Reader'),
        (EDITOR, 'Editor'),
        (JOURNALIST, 'Journalist'),
    ]

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER
    )

    # Reader-only fields:
    # These are used only when role == 'reader'.
    # If the user is a journalist or editor, these subscriptions are cleared
    # in the save() method below. This satisfies the task requirement that
    # journalist users should not keep reader subscription values.
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

    def save(self, *args, **kwargs):
        """
        Save the user and keep their group/role data consistent.

        A ManyToManyField cannot literally store None. The practical Django
        equivalent is to clear those relationships when they should not apply.

        Therefore:
        - Readers may have subscribed publishers and subscribed journalists.
        - Journalists and editors have those reader-only fields cleared.
        """
        super().save(*args, **kwargs)

        self.sync_role_group()

        if self.role != self.READER:
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

    def sync_role_group(self):
        """
        Put the user into the Django group matching their role.

        This supports the task requirement that users should be assigned to
        groups based on their role.
        """
        role_group_names = {
            self.READER: 'Reader',
            self.EDITOR: 'Editor',
            self.JOURNALIST: 'Journalist',
        }

        group_name = role_group_names.get(self.role)

        if not group_name:
            return

        group, created = Group.objects.get_or_create(name=group_name)

        self.groups.clear()
        self.groups.add(group)

    def __str__(self):
        return f'{self.username} ({self.role})'


class Publisher(models.Model):
    """
    Represents a publication.

    A publisher can have multiple editors and multiple journalists.
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
    """
    Represents a news article.

    An article is written by a journalist. It may optionally belong to a
    publisher. If publisher is blank, the article is treated as an independent
    journalist article.
    """

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

    approved = models.BooleanField(
        default=False,
        help_text='Indicates whether the article has been approved by an editor.'
    )

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Represents a curated collection of articles.

    Newsletters are created by journalists and can contain many articles.
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
    Stores records of approved articles.

    This model acts as the internal logging endpoint target for approved
    articles, matching the task requirement to log approved article activity.
    """

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='approval_logs'
    )

    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Approval log for {self.article.title}'