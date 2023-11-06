from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from users.forms import CustomUserCreationForm, CustomUserEditForm

# TODO Banned users functionality
# TODO Switch to CBVs


class CustomLoginView(auth_views.LoginView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, 'You are already logged in.')
            return HttpResponseRedirect(reverse('dashboard'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Successfully logged in!')
        return super().form_valid(form)


def custom_logout_then_login(request, *args, **kwargs):
    messages.success(request, 'Successfully logged out!')
    return auth_views.logout_then_login(request, *args, **kwargs)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            login(request, user)
            messages.success(request, 'You have successfully registered!')
            return redirect(reverse('dashboard'))
        return render(request, 'users/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def edit_user(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            user.save()
            messages.success(request, 'Successfully edited user info!')
            return redirect(reverse('dashboard'))
        return render(request, 'users/user_edit.html', {'form': form})
    else:
        form = CustomUserEditForm(initial=model_to_dict(user))
    return render(request, 'users/user_edit.html', {'form': form})


@login_required
def dashboard(request):
    user_posts = request.user.post_set.all()
    has_posts = user_posts.exists()
    context = {
        'user_posts': user_posts,
        'has_posts': has_posts
    }
    return render(request, 'users/dashboard.html', context=context)
