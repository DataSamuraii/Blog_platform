import logging

from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import redirect
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from social_core.exceptions import AuthForbidden
from social_django.middleware import SocialAuthExceptionMiddleware
from utils.utils import get_user_ip
from .models import VisitorGeoData

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


class GeoDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.get('geo_data_captured'):
            logger.info('Captured non-geo processed request, starting GeoDataMiddleware')
            ip = get_user_ip(request)
            g = GeoIP2()
            try:
                geo_data = g.city(ip)
                VisitorGeoData.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=ip, country=geo_data['country_name'], city=geo_data['city']
                )
                request.session['geo_data_captured'] = True
            except Exception as e:
                logger.error(f'Exception raised when running GeoDataMiddleware: {e}')
