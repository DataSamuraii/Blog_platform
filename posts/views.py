from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Category
from .forms import PostForm


def listing(request):
    context = {
        'posts': Post.objects.all(),
        'categories': Category.objects.all()
    }
    return render(request, 'posts/listing.html', context=context)


def view_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        if 'publish_button' in request.POST:
            post.is_published = True
            post.save()
            return redirect('view_post', post_id=post_id)

    post.views += 1
    post.save(update_fields=['views'])
    context = {
        'post': post
    }
    return render(request, 'posts/view_post.html', context=context)


def view_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    context = {
        'category': category,
        'posts': category.post_set.all()
    }
    return render(request, 'posts/view_category.html', context=context)


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


# TODO add update & delete views for posts
# TODO add update User info view
# TODO make post.views more resilient to abuse
