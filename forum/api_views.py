from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Q, Count
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostDetailSerializer, UserSerializer
from users.models import UserProfile


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostListAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta
        
        queryset = Post.objects.all()
        
        # Поиск
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(body__icontains=search) |
                Q(author__username__icontains=search)
            )
        
        # Фильтр по времени
        time_filter = self.request.query_params.get('time', '')
        if time_filter:
            now = timezone.now()
            if time_filter == 'today':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=1))
            elif time_filter == 'week':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
            elif time_filter == 'month':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
            elif time_filter == 'year':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=365))
        
        # Фильтр по минимальному количеству лайков
        min_likes = self.request.query_params.get('min_likes', '')
        if min_likes:
            try:
                min_likes_int = int(min_likes)
                queryset = queryset.annotate(like_count=Count('likes')).filter(like_count__gte=min_likes_int)
            except ValueError:
                pass
        
        # Сортировка
        sort_by = self.request.query_params.get('sort', 'newest')
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'popular':
            queryset = queryset.annotate(
                total_activity=Count('likes') + Count('comments')
            ).order_by('-total_activity', '-created_at')
        elif sort_by == 'most_commented':
            queryset = queryset.annotate(
                comment_count=Count('comments')
            ).order_by('-comment_count', '-created_at')
        elif sort_by == 'most_liked':
            queryset = queryset.annotate(
                like_count=Count('likes')
            ).order_by('-like_count', '-created_at')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]


class CommentListAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id).order_by('created_at')
    
    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(id=post_id)
        serializer.save(author=self.request.user, post=post)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_api(request, post_id):
    """API для лайка/дизлайка поста"""
    try:
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        
        return Response({
            'liked': liked,
            'total_likes': post.likes.count()
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_posts_api(request, user_id):
    """API для получения постов пользователя"""
    try:
        user = User.objects.get(id=user_id)
        posts = Post.objects.filter(author=user).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats_api(request):
    """API для статистики админа"""
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    banned_users = UserProfile.objects.filter(is_banned=True).count()
    
    return Response({
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'banned_users': banned_users
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_api(request):
    """API для поиска"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    posts = Post.objects.filter(
        Q(title__icontains=query) | 
        Q(body__icontains=query) |
        Q(author__username__icontains=query)
    ).order_by('-created_at')
    
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)