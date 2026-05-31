from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Article,
    ApprovedArticleLog,
    CustomUser,
    Newsletter,
    Publisher,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role and Subscriptions', {
            'fields': (
                'role',
                'subscribed_publishers',
                'subscribed_journalists',
            )
        }),
    )

    list_display = ('username', 'email', 'role', 'is_staff')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'publisher', 'created_at')
    search_fields = ('title', 'content')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'description')


@admin.register(ApprovedArticleLog)
class ApprovedArticleLogAdmin(admin.ModelAdmin):
    list_display = ('article', 'posted_at')
