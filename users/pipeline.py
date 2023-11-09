from social_core.exceptions import AuthForbidden


def check_ban_user(backend, details, response, user=None, *args, **kwargs):
    if user and user.is_banned:
        raise AuthForbidden(backend)
