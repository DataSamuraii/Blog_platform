from django.urls import path
from analytics import views

urlpatterns = [
    path('user_interaction/', views.UserInteractionView.as_view(), name='user_interaction')
]
