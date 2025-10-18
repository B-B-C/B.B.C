from .forms import PostForm, CommentForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from users.models import UserProfile
from django.utils import timezone

def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        ).order_by('-created_at')
    return render(request, 'forum/search_results.html', {'query': query, 'results': results})



def index(request):
    posts = Post.objects.order_by('-created_at')
    return render(request, 'forum/index.html', {'posts': posts})

def thread_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.order_by('created_at')

    if request.method == 'POST':
        if request.user.is_authenticated:
            # Check if user is banned
            try:
                profile = request.user.userprofile
                if profile.is_banned:
                    if profile.banned_until and profile.banned_until > timezone.now():
                        messages.error(request, f'Вы забанены до {profile.banned_until.strftime("%d.%m.%Y %H:%M")}. Причина: {profile.ban_reason or "Не указана"}')
                        return redirect('thread-detail', post_id=post.id)
                    elif not profile.banned_until:
                        messages.error(request, f'Вы забанены навсегда. Причина: {profile.ban_reason or "Не указана"}')
                        return redirect('thread-detail', post_id=post.id)
            except UserProfile.DoesNotExist:
                pass
            
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('thread-detail', post_id=post.id)
        else:
            form = CommentForm()
    else:
        form = CommentForm()
    
    return render(request, 'forum/thread_detail.html', {
        'post': post, 
        'comments': comments, 
        'comment_form': form
    })

@login_required
def new_post(request):
    # Check if user is banned
    try:
        profile = request.user.userprofile
        if profile.is_banned:
            if profile.banned_until and profile.banned_until > timezone.now():
                messages.error(request, f'Вы забанены до {profile.banned_until.strftime("%d.%m.%Y %H:%M")}. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('forum-index')
            elif not profile.banned_until:
                messages.error(request, f'Вы забанены навсегда. Причина: {profile.ban_reason or "Не указана"}')
                return redirect('forum-index')
    except UserProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('thread-detail', post_id=new_post.id)
    else:
        form = PostForm()
    return render(request, 'forum/new_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("Это не ваш пост.")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('thread-detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'forum/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return HttpResponseForbidden("Это не ваш пост.")

    if request.method == 'POST':
        post.delete()
        return redirect('forum-index')

    return render(request, 'forum/delete_post.html', {'post': post})

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.likes.count()})
