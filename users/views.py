import logging
from django.contrib.auth import get_user_model

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import get_object_or_404

from posts.models import Post
from .models import UnbanRequest
from .forms import CustomUserCreationForm, CustomUserEditForm, CustomAuthenticationForm, UnbanRequestForm

logger = logging.getLogger(__name__.split('.')[0])

# TODO Analytics: Track and analyze user interactions on your blog posts, like views, likes, and shares;
#  use this data to recommend posts to users or just for your insights.
# TODO Author Analytics Dashboard: Create a custom dashboard for authors to view the performance of their posts.


class CustomLoginView(auth_views.LoginView):
    form_class = CustomAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, 'You are already logged in.')
            return redirect('post_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully logged in!')
        logger.info(f"User {form.get_user().username} logged in, IP: {self.request.META['REMOTE_ADDR']}")
        return response

    def form_invalid(self, form):
        if getattr(self.request, 'banned', False):
            return redirect(reverse('banned_user'))

        response = super().form_invalid(form)
        logger.warning(
            f"Failed login attempt for {self.request.POST['username']}, IP: {self.request.META['REMOTE_ADDR']}")
        return response


class CustomLogoutView(LoginRequiredMixin, auth_views.LogoutView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'Successfully logged out!')
        logger.info(f"User {request.user.username} logged out")
        return response


class RegisterUserView(CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        response = super().form_valid(form)
        messages.success(self.request, 'You have successfully registered!')
        logger.info(f"New user registered: {user.username}")
        return response


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(self.model, pk=user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = self.object.post_set.filter(is_published=True)
        return context

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if self.request.user == obj:
            self.template_name = 'users/user_detail_dashboard.html'
        return super().get(request, *args, **kwargs)


class EditUserView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = CustomUserEditForm
    template_name = 'users/user_edit.html'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(self.model, pk=user_id)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully edited user info!')
        logger.info(f"User {self.request.user.username} changed fields: {form.changed_data}")
        return response

    def get_success_url(self):
        return reverse('user_detail', args=[self.object.id])


class BannedUserView(CreateView):
    model = UnbanRequest
    form_class = UnbanRequestForm
    template_name = 'users/banned_user.html'
    success_url = reverse_lazy('banned_user')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Your unban request has been received!')
        return response
