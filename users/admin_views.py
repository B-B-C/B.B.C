from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from forum.models import Post, Comment
from .models import UserProfile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
import json

@login_required
def admin_dashboard(request):
    """Custom admin dashboard accessible from main site"""
    # Check if user is admin
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('forum-index')
    
    # Get statistics
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    admin_users = UserProfile.objects.filter(is_admin=True).count()
    
    # Get recent activity
    recent_posts = Post.objects.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    stats = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'admin_users': admin_users,
    }
    
    return render(request, 'users/admin_dashboard.html', {
        'stats': stats,
        'recent_posts': recent_posts,
        'recent_users': recent_users,
    })

@login_required
def admin_users(request):
    """Manage users in admin dashboard"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('forum-index')
    
    search_query = request.GET.get('search', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    return render(request, 'users/admin_users.html', {
        'users': users_page,
        'search_query': search_query,
    })

@login_required
def admin_posts(request):
    """Manage posts in admin dashboard"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('forum-index')
    
    search_query = request.GET.get('search', '')
    posts = Post.objects.all()
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(body__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)
    
    return render(request, 'users/admin_posts.html', {
        'posts': posts_page,
        'search_query': search_query,
    })

@login_required
def admin_user_detail(request, user_id):
    """View and edit specific user details"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('forum-index')
    
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    user_comments = Comment.objects.filter(author=user).order_by('-created_at')
    
    return render(request, 'users/admin_user_detail.html', {
        'target_user': user,
        'profile': profile,
        'user_posts': user_posts,
        'user_comments': user_comments,
    })

@login_required
@require_POST
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
    })

@login_required
@require_POST
def admin_toggle_admin_status(request, user_id):
    """Toggle user admin status"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.is_admin = not profile.is_admin
    profile.save()
    
    return JsonResponse({
        'success': True,
        'is_admin': profile.is_admin,
        'message': f'User {"granted" if profile.is_admin else "revoked"} admin privileges'
    })

@login_required
@require_POST
def admin_delete_user(request, user_id):
    """Delete user (admin only)"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deleting themselves
    if user == request.user:
        return JsonResponse({'error': 'Cannot delete your own account'}, status=400)
    
    username = user.username
    user.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'User {username} deleted successfully'
    })

@login_required
@require_POST
def admin_delete_post(request, post_id):
    """Delete post (admin only)"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    post = get_object_or_404(Post, id=post_id)
    title = post.title
    post.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Post "{title}" deleted successfully'
    })

@login_required
@require_POST
def admin_ban_user(request, user_id):
    """Ban user (admin only)"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Prevent admin from banning themselves
    if user == request.user:
        return JsonResponse({'error': 'Cannot ban yourself'}, status=400)
    
    # Prevent banning other admins
    if profile.is_admin:
        return JsonResponse({'error': 'Cannot ban other administrators'}, status=400)
    
    data = json.loads(request.body)
    ban_reason = data.get('ban_reason', '')
    ban_duration = data.get('ban_duration', 'permanent')
    
    profile.is_banned = True
    profile.ban_reason = ban_reason
    
    if ban_duration != 'permanent':
        try:
            days = int(ban_duration)
            profile.banned_until = timezone.now() + timedelta(days=days)
        except ValueError:
            profile.banned_until = None
    else:
        profile.banned_until = None
    
    profile.save()
    
    return JsonResponse({
        'success': True,
        'message': f'User {user.username} has been banned',
        'ban_reason': ban_reason,
        'banned_until': profile.banned_until.isoformat() if profile.banned_until else None
    })

@login_required
@require_POST
def admin_unban_user(request, user_id):
    """Unban user (admin only)"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    profile.is_banned = False
    profile.ban_reason = None
    profile.banned_until = None
    profile.save()
    
    return JsonResponse({
        'success': True,
        'message': f'User {user.username} has been unbanned'
    })

@login_required
@require_POST
def admin_delete_comment(request, comment_id):
    """Delete comment (admin only)"""
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    comment = get_object_or_404(Comment, id=comment_id)
    content = comment.content[:50] + "..." if len(comment.content) > 50 else comment.content
    comment.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Comment "{content}" deleted successfully'
    })

