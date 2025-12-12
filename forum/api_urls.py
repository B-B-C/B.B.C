from django.urls import path
from . import api_views

urlpatterns = [
    # Posts API
    path('posts/', api_views.PostListAPIView.as_view(), name='api-post-list'),
    path('posts/<int:pk>/', api_views.PostDetailAPIView.as_view(), name='api-post-detail'),
    path('posts/<int:post_id>/like/', api_views.toggle_like_api, name='api-post-like'),
    
    # Comments API
    path('posts/<int:post_id>/comments/', api_views.CommentListAPIView.as_view(), name='api-comment-list'),
    
    # User API
    path('users/<int:user_id>/posts/', api_views.user_posts_api, name='api-user-posts'),
    
    # Admin API
    path('admin/stats/', api_views.admin_stats_api, name='api-admin-stats'),
    
    # Search API
    path('search/', api_views.search_api, name='api-search'),
]