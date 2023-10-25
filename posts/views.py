from django.shortcuts import render, get_object_or_404
from .models import Post, Category


def listing(request):
    context = {
        'posts': Post.objects.all(),
        'categories': Category.objects.all()
    }
    return render(request, 'posts/listing.html', context=context)


def view_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
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


#  TODO add view to publish posts