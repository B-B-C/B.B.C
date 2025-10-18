from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/posts/', admin_views.admin_posts, name='admin_posts'),
    path('admin/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/toggle-status/', admin_views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin/users/<int:user_id>/toggle-admin/', admin_views.admin_toggle_admin_status, name='admin_toggle_admin_status'),
    path('admin/users/<int:user_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
    path('admin/users/<int:user_id>/ban/', admin_views.admin_ban_user, name='admin_ban_user'),
    path('admin/users/<int:user_id>/unban/', admin_views.admin_unban_user, name='admin_unban_user'),
    path('admin/posts/<int:post_id>/delete/', admin_views.admin_delete_post, name='admin_delete_post'),
    path('admin/comments/<int:comment_id>/delete/', admin_views.admin_delete_comment, name='admin_delete_comment'),
]
