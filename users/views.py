from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from users.forms import CustomUserCreationForm


@login_required
def dashboard(request):
    user_posts = request.user.post_set.all()
    has_posts = user_posts.exists()
    context = {
        'user_posts': user_posts,
        'has_posts': has_posts
    }
    return render(request, 'users/dashboard.html', context=context)


def register(request):
    if request.method == 'GET':
        return render(request, 'users/register.html', {'form': CustomUserCreationForm})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            login(request, user)
            return redirect(reverse('dashboard'))
