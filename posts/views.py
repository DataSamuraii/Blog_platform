from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic.edit import FormView
from django.db import transaction

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


# TODO Turn into a CBV with only POST method, get rid of HTML > switch to JS pop-up on DELETE button click
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


class CreateCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'posts/create_category.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next', 'dashboard')
        if next_url.startswith('/'):
            return next_url
        return reverse_lazy(next_url)


class CreateCommentView(CreateView):
    model = Comment
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
            comment.parent_comment = parent_comment_id

        comment.save()
        messages.success(self.request, 'Successfully posted new comment!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            messages.error(self.request, errors)

        post_id = self.kwargs['post_id']
        return redirect('view_post', post_id)


class DeleteCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    # noinspection PyMethodMayBeStatic
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

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        reaction_type = request.POST.get('reaction_type')

        if reaction_type not in ['like', 'dislike']:
            return HttpResponseBadRequest('Invalid request')

        comment_id = kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)

        with transaction.atomic():
            self.handle_reaction(request.user, comment, reaction_type)

        return redirect('view_post', comment.post.id)

    # noinspection PyMethodMayBeStatic
    def handle_reaction(self, user, comment, reaction_type):
        reaction, created = CommentReaction.objects.get_or_create(
            user=user,
            comment=comment,
            defaults={'reaction_type': reaction_type}
        )

        if not created and reaction.reaction_type == reaction_type:
            reaction.delete()
        else:
            reaction.reaction_type = reaction_type
            reaction.save()
