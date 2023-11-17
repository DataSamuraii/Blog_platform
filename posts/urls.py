from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:post_id>/add_comment/<int:comment_id>', views.CreateCommentView.as_view(),
         name='add_comment_reply'),
    path('post/<int:post_id>/add_comment', views.CreateCommentView.as_view(), name='add_comment'),
    path('post/<int:post_id>/edit', views.EditPostView.as_view(), name='edit_post'),
    path('post/<int:post_id>/delete', views.DeletePostView.as_view(), name='delete_post'),
    path('post/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.CreatePostView.as_view(), name='create_post'),
    path('post/search/', views.SearchResultsView.as_view(), name='search_results'),
    path('category/<int:category_id>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/create/', views.CreateCategoryView.as_view(), name='category_create'),
    path('comment/<int:comment_id>/delete', views.DeleteCommentView.as_view(), name='comment_delete'),
    path('comment/<int:comment_id>/reaction', views.CommentReactionView.as_view(), name='comment_reaction')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
