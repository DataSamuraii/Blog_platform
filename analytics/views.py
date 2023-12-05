import json

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.views import View

from .models import UserInteraction


class UserInteractionView(View):
    http_method_names = ['post']

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        try:
            interactions_data = json.loads(request.body).get('interactions', [])
            interactions = [
                UserInteraction(
                    interaction_type=interaction['type'],
                    x_coordinate=interaction['x'], y_coordinate=interaction['y'],
                    timestamp=parse_datetime(interaction['timestamp']), page=interaction['page']
                ) for interaction in interactions_data
            ]
            UserInteraction.objects.bulk_create(interactions)
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'erros', 'message': str(e)}, status=400)

