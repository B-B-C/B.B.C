from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='forum-index'),
    path('post/<int:post_id>/', views.thread_detail, name='thread-detail'),
    path('post/new/', views.new_post, name='new-post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit-post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete-post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle-like'),
    path('search/', views.search, name='search'),
]
