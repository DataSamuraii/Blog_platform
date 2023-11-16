import logging
from datetime import timedelta

from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from users.admin import YearFilter
from .models import Post, Category, ViewedPost, Comment

logger = logging.getLogger(__name__.split('.')[0])


class AuthorLinkMixin:
    def author_link(self, obj):
        if obj.author:
            url = reverse('admin:users_customuser_change', args=[obj.author.id])
            return format_html('<a href="{}">{}</a>', url, obj.author)
        return '-'

    author_link.short_description = 'author'


class PostLinkMixin:
    def post_link(self, obj):
        if obj.post:
            url = reverse('admin:posts_post_change', args=[obj.post.id])
            return format_html('<a href="{}">{}</a>', url, obj.post)
        return '-'

    post_link.short_description = 'post'


class ViewsFilter(admin.SimpleListFilter):
    title = _('Views')
    parameter_name = 'views'

    def lookups(self, request, model_admin):
        return (
            ('-50', _('<50')),
            ('50-100', _('50-100')),
            ('100-1000', _('100-1000')),
            ('1000-', _('1000>')),
        )

    def queryset(self, request, queryset):
        if self.value() == '-50':
            return queryset.filter(views__lt=50)
        if self.value() == '50-100':
            return queryset.filter(views__gte=50, views__lt=100)
        if self.value() == '100-1000':
            return queryset.filter(views__gte=100, views__lt=1000)
        if self.value() == '1000-':
            return queryset.filter(views__gte=1000)
        return queryset


class PostYearFilter(YearFilter):
    data_field = 'date_published'


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title


@admin.register(Post)
class PostAdmin(AuthorLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'title', 'author_link', 'date_published', 'category_link', 'is_published', 'views']
    list_filter = [PostYearFilter, 'category', ViewsFilter, 'author', 'is_published']
    search_fields = ['title', 'content', 'category__title', 'author__username__iexact']

    form = PostAdminForm

    def category_link(self, obj):
        if obj.category:
            url = reverse('admin:posts_category_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category)
        return '-'

    category_link.short_description = 'category'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title', 'description']


@admin.register(ViewedPost)
class ViewedPostAdmin(PostLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'post_link', 'timestamp', 'ip_address']
    list_filter = ['post']
    search_fields = ['timestamp', 'ip_address']
    change_list_template = 'admin/viewedpost_change_list.html'

    def get_urls(self):
        my_urls = [
            path('purge_old_views/', self.purge_old_views, name='purge_old_views')
        ]
        return my_urls + super().get_urls()

    def purge_old_views(self, request):
        if not request.user.has_perm('posts.delete_viewedpost'):
            return HttpResponseForbidden('You do not have permission to perform this action.')

        logger.warning(f'purge_old_views action called by {request.user}')
        time_threshold = timezone.now() - timedelta(hours=24)
        old_records = ViewedPost.objects.filter(timestamp__lte=time_threshold)
        count = old_records.count()
        old_records.delete()
        self.message_user(request, f'Successfully deleted {count} old records')
        return HttpResponseRedirect(reverse('admin:posts_viewedpost_changelist'))


class CommentYearFilter(YearFilter):
    data_field = 'timestamp'


@admin.register(Comment)
class CommentAdmin(PostLinkMixin, AuthorLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'author_link', 'post_link', 'parent_comment_link', 'is_deleted', 'likes_count',
                    'dislikes_count']
    list_filter = [CommentYearFilter, 'post', 'is_deleted']
    search_fields = ['content', 'author', ]

    def parent_comment_link(self, obj):
        if obj.parent_comment:
            url = reverse('admin:posts_post_change', args=[obj.parent_comment.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent_comment)
        return '-'

    parent_comment_link.short_description = 'parent comment id'
