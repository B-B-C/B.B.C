from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .forms import UserRegisterForm, UserProfileForm, PasswordChangeForm, MessageForm, ReportForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forum.models import Post, Comment
from .models import UserProfile, Message, Report
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse

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


@login_required
def messages_list(request):
    """Список всех диалогов пользователя"""
    user = request.user
    
    # Получаем всех пользователей, с которыми есть переписка
    sent_messages = Message.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
    received_messages = Message.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
    
    # Объединяем всех собеседников
    all_conversations = set(list(sent_messages) + list(received_messages))
    
    # Получаем последнее сообщение для каждого диалога
    conversations = []
    for user_id in all_conversations:
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            continue  # Пропускаем удалённых пользователей
        
        last_message = Message.objects.filter(
            Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
        ).order_by('-created_at').first()
        
        unread_count = Message.objects.filter(
            sender=other_user, 
            recipient=user, 
            is_read=False
        ).count()
        
        conversations.append({
            'user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    # Сортируем по времени последнего сообщения
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(), reverse=True)
    
    return render(request, 'users/messages_list.html', {
        'conversations': conversations,
    })


@login_required
def conversation(request, user_id):
    """Просмотр диалога с конкретным пользователем"""
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user
    
    # Проверяем, не забанен ли пользователь
    try:
        profile = current_user.userprofile
        if profile.is_banned:
            if profile.banned_until and profile.banned_until > timezone.now():
                messages.error(request, f'Вы забанены до {profile.banned_until.strftime("%d.%m.%Y %H:%M")}. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('messages_list')
            elif not profile.banned_until:
                messages.error(request, f'Вы забанены навсегда. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('messages_list')
    except UserProfile.DoesNotExist:
        pass
    
    # Получаем все сообщения между пользователями
    message_list = Message.objects.filter(
        Q(sender=current_user, recipient=other_user) | Q(sender=other_user, recipient=current_user)
    ).order_by('created_at')
    
    # Помечаем входящие сообщения как прочитанные
    Message.objects.filter(sender=other_user, recipient=current_user, is_read=False).update(is_read=True)
    
    # Пагинация
    paginator = Paginator(message_list, 20)
    page_number = request.GET.get('page', 1)
    messages_page = paginator.get_page(page_number)
    
    # Форма для отправки сообщения
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=current_user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = current_user
            message.recipient = other_user
            message.save()
            messages.success(request, 'Сообщение отправлено!')
            return redirect('conversation', user_id=user_id)
    else:
        form = MessageForm(sender=current_user)
        form.fields['recipient_username'].initial = other_user.username
        form.fields['recipient_username'].widget.attrs['readonly'] = True
    
    return render(request, 'users/conversation.html', {
        'other_user': other_user,
        'messages': messages_page,
        'form': form,
    })


@login_required
def send_message(request, user_id=None):
    """Отправка нового сообщения"""
    current_user = request.user
    
    # Проверяем, не забанен ли пользователь
    try:
        profile = current_user.userprofile
        if profile.is_banned:
            if profile.banned_until and profile.banned_until > timezone.now():
                messages.error(request, f'Вы забанены до {profile.banned_until.strftime("%d.%m.%Y %H:%M")}. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('messages_list')
            elif not profile.banned_until:
                messages.error(request, f'Вы забанены навсегда. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('messages_list')
    except UserProfile.DoesNotExist:
        pass
    
    recipient = None
    if user_id:
        recipient = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=current_user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = current_user
            message.recipient = form.cleaned_data['recipient_username']
            message.save()
            messages.success(request, 'Сообщение отправлено!')
            return redirect('conversation', user_id=message.recipient.id)
    else:
        form = MessageForm(sender=current_user)
        if recipient:
            form.fields['recipient_username'].initial = recipient.username
    
    return render(request, 'users/send_message.html', {
        'form': form,
        'recipient': recipient,
    })


@login_required
def report_post(request, post_id):
    """Подача жалобы на пост"""
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, не забанен ли пользователь
    try:
        profile = request.user.userprofile
        if profile.is_banned:
            if profile.banned_until and profile.banned_until > timezone.now():
                messages.error(request, f'Вы забанены до {profile.banned_until.strftime("%d.%m.%Y %H:%M")}. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('thread-detail', post_id=post_id)
            elif not profile.banned_until:
                messages.error(request, f'Вы забанены навсегда. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('thread-detail', post_id=post_id)
    except UserProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ReportForm(request.POST, reporter=request.user, report_type='post', reported_post=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Жалоба отправлена администратору. Спасибо за обращение!')
            return redirect('thread-detail', post_id=post_id)
    else:
        form = ReportForm(reporter=request.user, report_type='post', reported_post=post)
    
    return render(request, 'users/report.html', {
        'form': form,
        'report_type': 'пост',
        'object': post,
        'back_url': reverse('thread-detail', args=[post_id]),
    })


@login_required
def report_comment(request, comment_id):
    """Подача жалобы на комментарий"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Проверяем, не забанен ли пользователь
    try:
        profile = request.user.userprofile
        if profile.is_banned:
            if profile.banned_until and profile.banned_until > timezone.now():
                messages.error(request, f'Вы забанены до {profile.banned_until.strftime("%d.%m.%Y %H:%M")}. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('thread-detail', post_id=comment.post.id)
            elif not profile.banned_until:
                messages.error(request, f'Вы забанены навсегда. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('thread-detail', post_id=comment.post.id)
    except UserProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ReportForm(request.POST, reporter=request.user, report_type='comment', reported_comment=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Жалоба отправлена администратору. Спасибо за обращение!')
            return redirect('thread-detail', post_id=comment.post.id)
    else:
        form = ReportForm(reporter=request.user, report_type='comment', reported_comment=comment)
    
    return render(request, 'users/report.html', {
        'form': form,
        'report_type': 'комментарий',
        'object': comment,
        'back_url': reverse('thread-detail', args=[comment.post.id]),
    })


@login_required
def report_user(request, user_id):
    """Подача жалобы на пользователя"""
    reported_user = get_object_or_404(User, id=user_id)
    
    # Проверяем, не забанен ли пользователь
    try:
        profile = request.user.userprofile
        if profile.is_banned:
            messages.error(request, f'Вы забанены. Причина: {profile.ban_reason or "Не указана"}')
            return redirect('forum-index')
    except UserProfile.DoesNotExist:
        pass
    
    # Нельзя жаловаться на самого себя
    if reported_user == request.user:
        messages.error(request, 'Вы не можете пожаловаться на самого себя.')
        return redirect('forum-index')
    
    if request.method == 'POST':
        form = ReportForm(request.POST, reporter=request.user, report_type='user', reported_user=reported_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Жалоба отправлена администратору. Спасибо за обращение!')
            return redirect('forum-index')
    else:
        form = ReportForm(reporter=request.user, report_type='user', reported_user=reported_user)
    
    return render(request, 'users/report.html', {
        'form': form,
        'report_type': 'пользователя',
        'object': reported_user,
        'back_url': reverse('forum-index'),
    })
