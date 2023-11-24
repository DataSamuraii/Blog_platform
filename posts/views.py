import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import PostForm, CategoryForm, CommentForm
from .models import Post, Category, ViewedPost, Comment, CommentReaction

logger = logging.getLogger(__name__.split('.')[0])


class SearchResultsView(ListView):
    model = Post
    template_name = 'posts/search_results.html'
    context_object_name = 'search_results'
    paginate_by = 3

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return Post.objects.filter(title__icontains=query)
        return Post.objects.none()


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(self.model, pk=post_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.filter(parent_comment__isnull=True).order_by(
            '-timestamp').prefetch_related('comment_set')
        context['form'] = CommentForm()
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.handle_views_counter()
        return response

    def handle_views_counter(self):
        # Check if the post was viewed from current IP in the last 24 hours
        ip = self.request.META.get('REMOTE_ADDR')
        time_threshold = timezone.now() - timedelta(hours=24)
        recent_views = ViewedPost.objects.filter(
            post=self.object, ip_address=ip, timestamp__gte=time_threshold
        )
        session_key = f'viewed_post_{self.object.id}'

        # Session-Based + IP-Based counting
        if not self.request.session.get(session_key) and not recent_views.exists():
            self.object.views += 1
            self.object.save(update_fields=['views'])
            self.request.session[session_key] = True
            self.request.session.set_expiry(86400)  # 24 hours in seconds
            ViewedPost.objects.create(post=self.object, ip_address=ip)
            logger.info(f'Created new ViewedPost for IP {ip}, post {self.object, self.object.pk}')


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully published a new post')
        logger.info(f'User {self.request.user} created new post {post.pk}')
        return response

    def get_success_url(self):
        return reverse('user_detail', args=[self.request.user.id])


class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_edit.html'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('post_detail', args=[self.object.id])

    def get_object(self, queryset=None):
        obj = get_object_or_404(self.model, pk=self.kwargs.get('post_id'))
        if obj.author != self.request.user:
            raise PermissionDenied("You don't have permission to delete this post.")
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully updated post!')
        logger.info(f'User {self.request.user} edited post {self.object.pk}')
        return response


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    http_method_names = ['post']

    def get_object(self, queryset=None):
        obj = get_object_or_404(self.model, pk=self.kwargs.get('post_id'))
        if obj.author != self.request.user:
            raise PermissionDenied("You don't have permission to delete this post.")
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully deleted post!')
        logger.warning(f'User {self.request.user} deleted post {self.object.pk}')
        return response

    def get_success_url(self):
        return reverse('user_detail', args=[self.request.user.id])


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'posts/category_detail.html'
    context_object_name = 'category'

    def get_object(self, queryset=None):
        category_id = self.kwargs.get('category_id')
        return get_object_or_404(self.model, pk=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.post_set.filter(is_published=True)
        return context


class CreateCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'posts/category_create.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next', 'post_list')
        if next_url.startswith('/'):
            return next_url
        return reverse_lazy(next_url)

    def form_valid(self, form):
        category = form.save(commit=False)
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully created a new category')
        logger.info(f'User {self.request.user} created new category {category.pk}')
        return response


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('post_detail', args=[post_id])

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        parent_comment_id = self.request.POST.get('reply_to_id')
        if parent_comment_id:
            comment.parent_comment = Comment.objects.get(pk=parent_comment_id)

        response = super().form_valid(form)
        messages.success(self.request, 'Successfully posted new comment!')
        logger.info(f'User {self.request.user} posted a new comment {comment.pk}')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            messages.error(self.request, errors)

        post_id = self.kwargs['post_id']
        return redirect('post_detail', post_id)


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    http_method_names = ['post']

    def get_object(self, queryset=None):
        obj = get_object_or_404(self.model, id=self.kwargs.get('comment_id'))
        if obj.author != self.request.user:
            raise PermissionDenied("You don't have permission to delete this post.")
        return obj

    def form_valid(self, form):
        self.object.is_deleted = True
        self.object.save()
        messages.success(self.request, 'Successfully deleted comment')
        logger.warning(f'User {self.request.user} deleted comment {self.object.pk}')
        return redirect('post_detail', self.object.post.id)


class CommentReactionView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs.get('comment_id'))

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        reaction_type = request.POST.get('reaction_type')

        if reaction_type not in ['like', 'dislike']:
            return HttpResponseBadRequest('Invalid request')

        comment = self.get_object()
        with transaction.atomic():
            self.handle_reaction(request.user, comment, reaction_type)
        messages.success(request, f'Successfully {reaction_type}d comment')
        return redirect('post_detail', comment.post.id)

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
