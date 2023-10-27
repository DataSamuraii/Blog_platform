from django.urls import path

from . import views

urlpatterns = [
    path('', views.listing, name='listing'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('category/<int:category_id>/', views.view_category, name='view_category'),
    path('create_post/', views.create_post, name='create_post'),
    path('create_category/', views.create_category, name='create_category'),
]
