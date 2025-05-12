from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Подписаться/отписаться от пользователя
    path('toggle/<str:username>/', views.SubscriptionToggleView.as_view(), name='toggle'),

    # Список подписчиков пользователя
    path('followers/<str:username>/', views.FollowersListView.as_view(), name='followers'),

    # Список подписок пользователя
    path('following/<str:username>/', views.FollowingListView.as_view(), name='following'),

    path('feed/', views.FeedView.as_view(), name='feed'),
]