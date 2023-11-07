from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from posts.models import Post
from .forms import CustomUserCreationForm, CustomUserEditForm


# TODO Banned users functionality
# TODO Add CAPTCHA to registration/login


class CustomLoginView(auth_views.LoginView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, 'You are already logged in.')
            return HttpResponseRedirect(reverse('dashboard'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Successfully logged in!')
        return super().form_valid(form)


class CustomLogoutView(auth_views.LogoutView):
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'Successfully logged out!')
        return response


class RegisterUserView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        response = super().form_valid(form)
        messages.success(self.request, 'You have successfully registered!')
        return response


class EditUserView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserEditForm
    template_name = 'users/user_edit.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully edited user info!')
        return response


class DashboardView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'users/dashboard.html'
    context_object_name = 'user_posts'

    def get_queryset(self):
        return self.request.user.post_set.all()
