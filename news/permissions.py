from rest_framework import permissions


class ArticlePermission(permissions.BasePermission):
    """
    API permissions for articles.

    Rules:
    - Readers can only view approved articles.
    - Journalists can create articles.
    - Journalists can edit/delete only their own articles.
    - Editors can view, update, delete, and approve articles.
    - Superusers can do everything.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return request.method in permissions.SAFE_METHODS

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST':
            return user.role == 'journalist'

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return user.role in ['journalist', 'editor']

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return (
                request.method in permissions.SAFE_METHODS
                and obj.approved
            )

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            if user.role == 'editor':
                return True

            if user.role == 'journalist':
                return obj.author == user or obj.approved

            return obj.approved

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if user.role == 'editor':
                return True

            if user.role == 'journalist':
                return obj.author == user

        return False


class IsEditor(permissions.BasePermission):
    """
    Allows access only to editors and superusers.

    Used for article approval endpoints.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (user.role == 'editor' or user.is_superuser)
        )