from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsReader(BasePermission):
    """
    Allows access only to users with the reader role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'reader'


class IsEditor(BasePermission):
    """
    Allows access only to editors or superusers.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.role == 'editor'
                or request.user.is_superuser
            )
        )


class IsJournalist(BasePermission):
    """
    Allows access only to journalists.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'journalist'
        )


class ArticlePermission(BasePermission):
    """
    Role-based article API permissions.

    Readers:
    - Can only view approved articles.

    Journalists:
    - Can create articles.
    - Can update and delete their own articles.

    Editors:
    - Can view, update, approve, and delete articles.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == 'POST':
            return request.user.role == 'journalist'

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.role in ['editor', 'journalist']

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return obj.approved or request.user.role in ['editor', 'journalist']

        if request.user.role == 'editor':
            return True

        if request.user.role == 'journalist':
            return obj.author == request.user

        return False