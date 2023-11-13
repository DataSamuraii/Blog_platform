import logging

from django.shortcuts import redirect
from django.urls import resolve
from social_core.exceptions import AuthForbidden
from social_django.middleware import SocialAuthExceptionMiddleware

logger = logging.getLogger(__name__.split('.')[0])


class AdminLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith('/admin/'):
            resolved_path = resolve(request.path_info)
            logger.info(
                f'Admin action by {request.user}: {request.method} {request.path} '
                f'Resolved {resolved_path.url_name} with args {resolved_path.args} and kwargs {resolved_path.kwargs}')

        return response


class SocialAuthBanMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        response = super().process_exception(request, exception)

        if isinstance(exception, AuthForbidden):
            return redirect('banned_user')
        return response
