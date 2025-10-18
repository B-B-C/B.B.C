from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .forms import UserRegisterForm, UserProfileForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forum.models import Post, Comment
from .models import UserProfile
from django.core.paginator import Paginator

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('forum-index')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('forum-index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('forum-index')


@login_required
def profile(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination for posts
    post_paginator = Paginator(user_posts, 5)
    post_page = request.GET.get('post_page')
    posts = post_paginator.get_page(post_page)
    
    # Pagination for comments
    comment_paginator = Paginator(user_comments, 5)
    comment_page = request.GET.get('comment_page')
    comments = comment_paginator.get_page(comment_page)
    
    return render(request, 'users/profile.html', {
        'posts': posts,
        'comments': comments,
        'user_posts': user_posts,  # Keep for backward compatibility
    })

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Update user fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Update profile fields
            profile.bio = form.cleaned_data['bio']
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
        form.fields['bio'].initial = profile.bio
        form.fields['avatar'].initial = profile.avatar
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def dashboard(request):
    """Personal dashboard with user activity history"""
    user = request.user
    
    # Get user's posts
    user_posts = Post.objects.filter(author=user).order_by('-created_at')[:10]
    
    # Get user's comments
    user_comments = Comment.objects.filter(author=user).order_by('-created_at')[:10]
    
    # Get liked posts
    liked_posts = Post.objects.filter(likes=user).order_by('-created_at')[:10]
    
    # Statistics
    stats = {
        'total_posts': Post.objects.filter(author=user).count(),
        'total_comments': Comment.objects.filter(author=user).count(),
        'total_likes_received': sum(post.likes.count() for post in user_posts),
        'total_likes_given': liked_posts.count(),
    }
    
    return render(request, 'users/dashboard.html', {
        'user_posts': user_posts,
        'user_comments': user_comments,
        'liked_posts': liked_posts,
        'stats': stats,
    })
