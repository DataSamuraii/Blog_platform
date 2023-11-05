from django.urls import path, include
from users import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_then_login, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
]
