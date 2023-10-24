from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('posts.urls')),
    path('account/', include('users.urls')),
]
