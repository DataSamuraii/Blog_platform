import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger(__name__.split('.')[0])


class CustomLoginBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                if user.is_banned:
                    request.banned = True
                    logger.info(f'Banned user {user} caught trying to login')
                    return None
                return user
        except user_model.DoesNotExist:
            return None
