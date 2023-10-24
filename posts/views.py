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


#  TODO add Category view, link to a separate view on a specific category with posts attached to that category
