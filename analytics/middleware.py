import logging

from django.contrib.gis.geoip2 import GeoIP2
from django.utils.deprecation import MiddlewareMixin

from utils.utils import get_user_ip
from .models import VisitorGeoData, VisitorPageData
from .tasks import log_page_visit

logger = logging.getLogger(__name__.split('.')[0])


class GeoDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.get('geo_data_captured'):
            logger.info('Captured non-geoprocessed request, starting GeoDataMiddleware')
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


class PageDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path.startswith('/admin/'):
            logger.info('Starting PageDataMiddleware')
            ip = get_user_ip(request)
            try:
                VisitorPageData.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=ip, page=request.path
                )

                # ALTERNATIVELY: Celery async task
                # log_page_visit.delay(
                #     user_id=request.user if request.user.is_authenticated else None,
                #     ip_address=ip, page=request.path
                # )
            except Exception as e:
                logger.error(f'Exception raised when running PageDataMiddleware: {e}')