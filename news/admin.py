from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    ApprovedArticleLog,
    Article,
    CustomUser,
    Newsletter,
    Publisher,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom user model.

    Adds the role and subscription fields to the Django admin.
    """

    fieldsets = UserAdmin.fieldsets + (
        (
            'News Application Role Information',
            {
                'fields': (
                    'role',
                    'subscribed_publishers',
                    'subscribed_journalists',
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'News Application Role Information',
            {
                'fields': (
                    'email',
                    'role',
                )
            },
        ),
    )

    list_display = [
        'username',
        'email',
        'role',
        'is_staff',
        'is_superuser',
    ]

    list_filter = [
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'username',
        'email',
    ]

    filter_horizontal = [
        'groups',
        'user_permissions',
        'subscribed_publishers',
        'subscribed_journalists',
    ]


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Admin configuration for publishers.
    """

    list_display = [
        'name',
        'description',
    ]

    search_fields = [
        'name',
    ]

    filter_horizontal = [
        'editors',
        'journalists',
    ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for articles.
    """

    list_display = [
        'title',
        'author',
        'publisher',
        'approved',
        'created_at',
    ]

    list_filter = [
        'approved',
        'publisher',
        'created_at',
    ]

    search_fields = [
        'title',
        'content',
        'author__username',
        'publisher__name',
    ]

    readonly_fields = [
        'created_at',
    ]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin configuration for newsletters.
    """

    list_display = [
        'title',
        'author',
        'created_at',
    ]

    list_filter = [
        'created_at',
        'author',
    ]

    search_fields = [
        'title',
        'description',
        'author__username',
    ]

    filter_horizontal = [
        'articles',
    ]

    readonly_fields = [
        'created_at',
    ]


@admin.register(ApprovedArticleLog)
class ApprovedArticleLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for approved article logs.
    """

    list_display = [
        'article',
        'posted_at',
    ]

    list_filter = [
        'posted_at',
    ]

    search_fields = [
        'article__title',
    ]

    readonly_fields = [
        'posted_at',
    ]
