from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/', views.PostCommentView.as_view(), name='post-comment'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<int:parent_id>/reply/', views.CommentReplyView.as_view(), name='comment-reply'),
    path('comments/<int:pk>/react/', views.comment_react, name='comment-react'),
    path('comments/<int:pk>/update/', views.comment_update, name='comment-update'),
    path('comment/<int:comment_id>/user-reactions/', views.user_reactions, name='user-reactions'),
    path('<int:pk>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('tag/<slug:slug>/', views.TagPostListView.as_view(), name='tag-posts'),
    path('<int:pk>/dislike/', views.PostDislikeView.as_view(), name='post-dislike'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]