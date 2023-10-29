from django.urls import path

from . import views

urlpatterns = [
    path('', views.listing, name='listing'),
    path('post/<int:post_id>/add_comment/<int:comment_id>', views.CreateCommentView.as_view(),
         name='add_comment_reply'),
    path('post/<int:post_id>/add_comment', views.CreateCommentView.as_view(), name='add_comment'),
    path('post/<int:post_id>/edit', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete', views.delete_post, name='delete_post'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:category_id>/', views.view_category, name='view_category'),
    path('comment/<int:comment_id>/delete', views.DeleteCommentView.as_view(), name='delete_comment'),

]
