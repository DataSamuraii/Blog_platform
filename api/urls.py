from django.urls import path

from . import views

urlpatterns = [
    path('posts/', views.PostList.as_view(), name='api_post_list'),
    path('posts/<int:pk>/', views.PostDetails.as_view(), name='api_post_details'),
    path('categories/', views.CategoryList.as_view(), name='api_categories_list'),
    path('categories/<int:pk>/', views.CategoryDetails.as_view(), name='api_categories_details'),
    path('comments/', views.CommentList.as_view(), name='api_comments_list'),
    path('comments/<int:pk>/', views.CommentDetails.as_view(), name='api_comments_details'),
    path('comment_reactions/', views.CommentReactionList.as_view(), name='api_comment_reactions_list'),
    path('comment_reactions/<int:pk>/', views.CommentReactionDetails.as_view(), name='api_comment_reactions_details'),

    path('users/', views.UserList.as_view(), name='api_users_list'),
    path('users/<int:pk>/', views.UserDetails.as_view(), name='api_users_details'),
    path('email_subscribers/', views.EmailSubscriberList.as_view(), name='api_email_subscribers_list'),
    path('email_subscribers/<int:pk>/', views.EmailSubscriberDetails.as_view(), name='api_email_subscribers_details'),
    path('unban_requests/', views.UnbanRequestList.as_view(), name='api_unban_requests_list'),
    path('unban_requests/<int:pk>/', views.UnbanRequestDetails.as_view(), name='api_unban_requests_details'),
]
