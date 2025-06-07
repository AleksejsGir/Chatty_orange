# posts/urls.py
from django.urls import include, path
from . import views # Импортируем views, хотя их пока нет

app_name = 'posts' # Определяем пространство имен URL

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/', views.PostCommentView.as_view(), name='post-comment'),  # Новый URL
    # path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    # path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment-update'),
    # Комментарии
    path('comments/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment-edit'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<int:parent_id>/reply/', views.CommentReplyView.as_view(), name='comment-reply'),
    path('comments/<int:pk>/react/', views.add_reaction_to_comment, name='comment-react'),
    path('<int:pk>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('tag/<slug:slug>/', views.TagPostListView.as_view(), name='tag-posts'),
    path('<int:pk>/dislike/', views.PostDislikeView.as_view(), name='post-dislike'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),

]
