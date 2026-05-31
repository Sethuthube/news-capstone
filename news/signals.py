from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Article, CustomUser, Newsletter


ROLE_GROUPS = {
    CustomUser.READER: 'Reader',
    CustomUser.EDITOR: 'Editor',
    CustomUser.JOURNALIST: 'Journalist',
}


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    """
    Create default user groups and assign permissions after migrations.
    """

    reader_group, _ = Group.objects.get_or_create(name='Reader')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    journalist_group, _ = Group.objects.get_or_create(name='Journalist')

    article_permissions = Permission.objects.filter(
        content_type__app_label='news',
        content_type__model='article'
    )

    newsletter_permissions = Permission.objects.filter(
        content_type__app_label='news',
        content_type__model='newsletter'
    )

    view_article = article_permissions.filter(codename='view_article').first()
    add_article = article_permissions.filter(codename='add_article').first()
    change_article = article_permissions.filter(
        codename='change_article'
    ).first()
    delete_article = article_permissions.filter(
        codename='delete_article'
    ).first()

    view_newsletter = newsletter_permissions.filter(
        codename='view_newsletter'
    ).first()
    add_newsletter = newsletter_permissions.filter(
        codename='add_newsletter'
    ).first()
    change_newsletter = newsletter_permissions.filter(
        codename='change_newsletter'
    ).first()
    delete_newsletter = newsletter_permissions.filter(
        codename='delete_newsletter'
    ).first()

    reader_permissions = [
        view_article,
        view_newsletter,
    ]

    editor_permissions = [
        view_article,
        change_article,
        delete_article,
        view_newsletter,
        change_newsletter,
        delete_newsletter,
    ]

    journalist_permissions = [
        view_article,
        add_article,
        change_article,
        delete_article,
        view_newsletter,
        add_newsletter,
        change_newsletter,
        delete_newsletter,
    ]

    reader_group.permissions.set(
        permission for permission in reader_permissions if permission
    )

    editor_group.permissions.set(
        permission for permission in editor_permissions if permission
    )

    journalist_group.permissions.set(
        permission for permission in journalist_permissions if permission
    )


@receiver(post_save, sender=CustomUser)
def assign_user_to_role_group(sender, instance, **kwargs):
    """
    Automatically place a user into the correct group based on their role.
    """

    group_name = ROLE_GROUPS.get(instance.role)

    if not group_name:
        return

    role_group = Group.objects.get(name=group_name)

    instance.groups.clear()
    instance.groups.add(role_group)