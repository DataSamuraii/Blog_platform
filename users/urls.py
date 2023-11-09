from django.urls import path, include

from users import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('edit_user/', views.EditUserView.as_view(), name='edit_user'),
    path('banned_user/', views.BannedUserView.as_view(), name='banned_user'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
]
