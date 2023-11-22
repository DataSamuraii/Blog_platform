from django.urls import path, include

from users import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('user/<int:user_id>/edit/', views.EditUserView.as_view(), name='edit_user'),
    path('user/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('email_subscription/add/', views.CreateEmailSubscriber.as_view(), name='create_email_subscriber'),
    path('email_subscription/delete/', views.DeleteEmailSubscriber.as_view(), name='delete_email_subscriber'),
    path('banned_user/', views.BannedUserView.as_view(), name='banned_user'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
]
