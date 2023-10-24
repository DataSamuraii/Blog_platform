from django.urls import path

from . import views

urlpatterns = [
    path('', views.listing, name='listing'),
    path('<int:post_id>', views.view_post, name='view_post')
]
