from django.shortcuts import redirect
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthForbidden


class SocialAuthBanMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        response = super().process_exception(request, exception)

        if isinstance(exception, AuthForbidden):
            return redirect('banned_user')
        return response
