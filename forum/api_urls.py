from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

urlpatterns = [
    path('posts/', api_views.PostListCreateView.as_view(), name='api-post-list'),
    path('posts/<int:pk>/', api_views.PostDetailView.as_view(), name='api-post-detail'),
    path('posts/<int:post_id>/comments/', api_views.CommentListCreateView.as_view(), name='api-comment-list'),
    path('posts/<int:post_id>/like/', api_views.toggle_like, name='api-toggle-like'),
    path('search/', api_views.search_posts, name='api-search'),
]

