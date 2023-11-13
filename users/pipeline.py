import logging

from social_core.exceptions import AuthForbidden

logger = logging.getLogger(__name__.split('.')[0])


def check_ban_user(backend, details, response, user=None, *args, **kwargs):
    if user and user.is_banned:
        logger.info(f'Banned user {user} caught trying to socialAuth login - raising {AuthForbidden}')
        raise AuthForbidden(backend)
