from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from datetime import timedelta

from .models import Post, Category, ViewedPost, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


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
