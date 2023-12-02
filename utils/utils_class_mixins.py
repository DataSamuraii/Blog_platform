from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html


class UserLinkMixin:
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_customuser_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return '-'

    user_link.short_description = 'user'


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


class YearFilter(admin.SimpleListFilter):
    title = 'year'
    parameter_name = 'year'
    data_field = 'date_joined'

    def lookups(self, request, model_admin):
        current_year = timezone.now().year
        return [(str(year), str(year)) for year in range(2020, current_year + 1)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{f'{self.data_field}__year': self.value()})
        return queryset
