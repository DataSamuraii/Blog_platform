from django.urls import path

from . import views

urlpatterns = [
    path('', views.listing, name='listing'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('category/<int:category_id>/', views.view_category, name='view_category'),
    path('create/', views.create_post, name='create_post')
]
