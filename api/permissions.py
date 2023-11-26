from rest_framework import permissions


class HasAddPostPermission(permissions.BasePermission):
    """
    Custom permission that allows publishing posts only to Author admin group members
    """
    message = "Only authorized authors are allowed to publish posts."

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.has_perm('posts.add_post')


class PostPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('posts.change_post')

        return False


class CommentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('posts.change_comment')

        return False


class CommentReactionPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('posts.change_commentreaction')

        return False


class HasViewUserPermission(permissions.BasePermission):
    """
    Custom permission that allows all users to send POST requests but
    only allows users with 'Can view user' permission to send GET requests.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True

        return request.user.has_perm('users.view_customuser')


class CustomUserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm('users.view_customuser')

        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('users.change_customuser')

        return False


class HasViewEmailSubscriberPermission(permissions.BasePermission):
    """
    Custom permission that allows all users to send POST requests but
    only allows users with 'Can view emailsubscriber' permission to send GET requests.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True

        return request.user.has_perm('users.view_emailsubscriber')


class EmailSubscriberPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm('users.view_emailsubscriber')

        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('users.change_emailsubscriber')

        return False


class HasViewUnbanRequestPermission(permissions.BasePermission):
    """
    Custom permission that allows all users to send POST requests but
    only allows users with 'Can view unbanrequest' permission to send GET requests.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True

        return request.user.has_perm('users.view_unbanrequest')


class UnbanRequestPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm('users.view_unbanrequest')

        if request.method in ['PUT', 'PATCH']:
            return request.user.has_perm('users.change_unbanrequest')

        return False
