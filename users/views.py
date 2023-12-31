import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import CustomUserCreationForm, CustomUserEditForm, CustomAuthenticationForm, UnbanRequestForm, \
    EmailSubscriberForm
from .models import UnbanRequest, EmailSubscriber

logger = logging.getLogger(__name__.split('.')[0])


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
    context_object_name = 'user'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(self.model, pk=user_id)

    def get_template_names(self):
        if self.request.user == self.object:
            return 'users/user_detail_dashboard.html'
        return 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = self.object.post_set.all()
        context['user_posts'] = user_posts
        if self.request.user == self.object:
            context['post_views_and_comments'] = json.dumps(
                [(post.title, post.views, post.comment_set.count()) for post in user_posts]
            )
            context['is_subscribed'] = hasattr(self.object, 'email_subscriber')
        return context


class EditUserView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = CustomUserEditForm
    template_name = 'users/user_edit.html'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(self.model, pk=user_id)

    def get_success_url(self):
        return reverse('user_detail', args=[self.object.id])

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully edited user info!')
        logger.info(f"User {self.request.user.username} changed fields: {form.changed_data}")
        return response


class CreateEmailSubscriber(LoginRequiredMixin, CreateView):
    model = EmailSubscriber
    form_class = EmailSubscriberForm
    http_method_names = ['post']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully added to email subscription list!')
        logger.info(f"User {self.request.user.username} added to email subscription")
        return response

    def get_success_url(self):
        return reverse('user_detail', args=[self.object.user.id])


class DeleteEmailSubscriber(LoginRequiredMixin, DeleteView):
    model = EmailSubscriber
    template_name = 'users/email_subscriber_delete.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.model.objects.get(user=request.user)
        except self.model.DoesNotExist:
            messages.info(request, 'You are not subscribed.')
            return redirect('user_detail', request.user.id)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = get_object_or_404(self.model, user=self.request.user)
        if obj.user != self.request.user:
            raise PermissionDenied("You don't have permission to unsubscribe this account.")
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully removed from email subscription list.')
        logger.info(f"User {self.request.user.username} removed from email subscription")
        return response

    def get_success_url(self):
        return reverse('user_detail', args=[self.object.user.id])


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
        logger.info(f"User {obj.user} submitted unban request")
        return response
