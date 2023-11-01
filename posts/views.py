from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic.edit import FormView

from .forms import PostForm, CategoryForm, CommentForm
from .models import Post, Category, ViewedPost, Comment, CommentReaction


# TODO add registering/authing with 3-party services (Gmail, GitHub)


def listing(request):
    context = {
        'posts': Post.objects.all(),
        'categories': Category.objects.all(),
    }
    return render(request, 'posts/listing.html', context=context)


def view_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # Check if the post was viewed from current IP in the last 24 hours
    ip = request.META.get('REMOTE_ADDR')
    time_threshold = timezone.now() - timedelta(hours=24)
    recent_views = ViewedPost.objects.filter(
        post=post, ip_address=ip, timestamp__gte=time_threshold
    )
    session_key = f'viewed_post_{post_id}'
    # Session-Based + IP-Based counting
    if not request.session.get(session_key, False) and not recent_views.exists():
        post.views += 1
        post.save(update_fields=['views'])
        request.session[session_key] = True
        request.session.set_expiry(86400)  # 24 hours in seconds
        ViewedPost.objects.create(post=post, ip_address=ip)

    form = CommentForm()
    context = {
        'post': post,
        'comments': post.comment_set.filter(post=post_id, parent_comment__isnull=True).order_by(
            '-timestamp').prefetch_related('comment_set'),
        'form': form
    }
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
        return render(request, 'posts/edit_post.html', {'form': form})
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


class CommentView(FormView):
    form_class = CommentForm
    http_method_names = ['post']

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('view_post', args=[post_id])

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        parent_comment_id = self.request.POST.get('reply_to_id')
        if parent_comment_id:
            parent_comment = get_object_or_404(Comment, id=parent_comment_id)
            comment.parent_comment = parent_comment

        comment.save()
        messages.success(self.request, 'Successfully posted new comment!')
        return super().form_valid(form)


class DeleteCommentView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.author:
            comment.is_deleted = True
            comment.save()
            messages.success(request, 'Successfully deleted comment')
        else:
            return HttpResponseForbidden("You don't have permission to edit this post.")

        return redirect('view_post', comment.post.id)


class CommentReactionView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        reaction_type = request.POST.get('reaction_type')

        if reaction_type not in ['like', 'dislike']:
            return HttpResponseBadRequest('Invalid request')

        comment_id = kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if the user has already reacted to this comment
        reaction, created = CommentReaction.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'reaction_type': reaction_type}
        )

        if not created and reaction.reaction_type == reaction_type:
            reaction.delete()
        else:
            reaction.reaction_type = reaction_type
            reaction.save()

        return redirect('view_post', comment.post.id)
