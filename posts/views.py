from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseForbidden


from .models import Post, Category, ViewedPost
from .forms import PostForm, CategoryForm


def listing(request):
    context = {
        'posts': Post.objects.all(),
        'categories': Category.objects.all()
    }
    return render(request, 'posts/listing.html', context=context)


def view_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    session_key = f'viewed_post_{post_id}'

    # Check if the post was viewed from current IP in the last 24 hours
    ip = request.META.get('REMOTE_ADDR')
    time_threshold = timezone.now() - timedelta(hours=24)
    recent_views = ViewedPost.objects.filter(
        post=post, ip_address=ip, timestamp__gte=time_threshold
    )

    if request.method == 'POST':
        if 'publish_button' in request.POST:
            post.is_published = True
            post.save()
            return redirect('view_post', post_id=post_id)

    # Session-Based + IP-Based counting
    if not request.session.get(session_key, False) and not recent_views.exists():
        post.views += 1
        post.save(update_fields=['views'])
        request.session[session_key] = True
        request.session.set_expiry(86400)  # 24 hours in seconds
        ViewedPost.objects.create(post=post, ip_address=ip)

    context = {'post': post}
    return render(request, 'posts/view_post.html', context=context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('dashboard')
        return render(request, 'posts/create_post.html', {'form': form})
    else:
        form = PostForm(initial={'author': request.user.id})
    return render(request, 'posts/create_post.html', {'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("You don't have permission to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated post!')
            return redirect('view_post', post_id=post_id)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post
    }
    return render(request, 'posts/edit_post.html', context=context)


def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("You don't have permission to edit this post.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Successfully deleted post!')
        return redirect('dashboard')

    context = {'post': post}
    return render(request, 'posts/delete_post.html', context=context)


def view_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    context = {
        'category': category,
        'posts': category.post_set.all()
    }
    return render(request, 'posts/view_category.html', context=context)


@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        return render(request, 'posts/create_category.html', {'form': form})
    else:
        form = CategoryForm()
        return render(request, 'posts/create_category.html', {'form': form})

# TODO add commenting
# TODO add registering/authing with 3-party services (Gmail, GitHub)
