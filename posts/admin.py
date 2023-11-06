from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django import forms

from .models import Post, Category, ViewedPost, Comment


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
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_published', 'category_link', 'author_link', 'is_published', 'views')
    list_filter = ('category', 'author', 'is_published', ViewsFilter)
    search_fields = ['title', 'content', 'category__title', 'author__username__iexact']
    form = PostAdminForm

    def category_link(self, obj):
        if obj.category:
            url = reverse('admin:posts_category_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category)
        return '-'
    category_link.short_description = 'category'

    def author_link(self, obj):
        if obj.author:
            url = reverse('admin:auth_user_change', args=[obj.author.id])
            return format_html('<a href="{}">{}</a>', url, obj.author)
        return '-'
    author_link.short_description = 'author'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ViewedPost)
class ViewedPostAdmin(admin.ModelAdmin):
    change_list_template = 'admin/viewedpost_change_list.html'

    def get_urls(self):
        my_urls = [
            path('purge_old_views/', self.purge_old_views, name='purge_old_views')
        ]
        return my_urls + super().get_urls()

    def purge_old_views(self, request):
        time_threshold = timezone.now() - timedelta(hours=24)
        old_records = ViewedPost.objects.filter(timestamp__lte=time_threshold)
        count = old_records.count()
        old_records.delete()
        self.message_user(request, f'Successfully deleted {count} old records')
        return HttpResponseRedirect(reverse('admin:posts_viewedpost_changelist'))


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
