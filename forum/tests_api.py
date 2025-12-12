"""
API Integration Tests
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Comment
from users.models import UserProfile


class JWTAuthenticationTest(TestCase):
    """Tests for JWT authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
    
    def test_register_api(self):
        """Test user registration with JWT tokens"""
        url = reverse('api-register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_api(self):
        """Test login with JWT tokens"""
        url = reverse('api-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('api-login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_token_refresh(self):
        """Test token refresh endpoint"""
        refresh = RefreshToken.for_user(self.user)
        url = reverse('api-token-refresh-custom')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_logout_api(self):
        """Test logout with token blacklisting"""
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        
        # Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        
        # Logout
        url = reverse('api-logout')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PostAPITest(TestCase):
    """Tests for Post API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_post(self):
        """Test creating a post via API"""
        url = reverse('api-post-list')
        data = {
            'title': 'Test Post',
            'body': 'This is a test post'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'Test Post')
    
    def test_list_posts(self):
        """Test listing posts"""
        Post.objects.create(
            title='Post 1',
            body='Body 1',
            author=self.user
        )
        Post.objects.create(
            title='Post 2',
            body='Body 2',
            author=self.user
        )
        
        url = reverse('api-post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_post_detail(self):
        """Test getting post details"""
        post = Post.objects.create(
            title='Test Post',
            body='Test body',
            author=self.user
        )
        
        url = reverse('api-post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
    
    def test_update_post(self):
        """Test updating a post"""
        post = Post.objects.create(
            title='Original Title',
            body='Original body',
            author=self.user
        )
        
        url = reverse('api-post-detail', kwargs={'pk': post.id})
        data = {
            'title': 'Updated Title',
            'body': 'Updated body'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, 'Updated Title')
    
    def test_delete_post(self):
        """Test deleting a post"""
        post = Post.objects.create(
            title='Test Post',
            body='Test body',
            author=self.user
        )
        
        url = reverse('api-post-detail', kwargs={'pk': post.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)
    
    def test_post_search(self):
        """Test post search functionality"""
        Post.objects.create(title='Django Post', body='Content', author=self.user)
        Post.objects.create(title='Python Post', body='Content', author=self.user)
        Post.objects.create(title='JavaScript Post', body='Content', author=self.user)
        
        url = reverse('api-post-list')
        response = self.client.get(url, {'search': 'Django'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django Post')
    
    def test_post_sorting(self):
        """Test post sorting"""
        post1 = Post.objects.create(title='First', body='Content', author=self.user)
        post2 = Post.objects.create(title='Second', body='Content', author=self.user)
        
        url = reverse('api-post-list')
        response = self.client.get(url, {'sort': 'oldest'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], post1.id)


class CommentAPITest(TestCase):
    """Tests for Comment API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.post = Post.objects.create(
            title='Test Post',
            body='Test body',
            author=self.user
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_comment(self):
        """Test creating a comment"""
        url = reverse('api-comment-list', kwargs={'post_id': self.post.id})
        data = {
            'content': 'This is a test comment'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, 'This is a test comment')
    
    def test_list_comments(self):
        """Test listing comments for a post"""
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Comment 1'
        )
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Comment 2'
        )
        
        url = reverse('api-comment-list', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class LikeAPITest(TestCase):
    """Tests for Like API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.post = Post.objects.create(
            title='Test Post',
            body='Test body',
            author=self.user
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_toggle_like(self):
        """Test toggling like on a post"""
        url = reverse('api-post-like', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['total_likes'], 1)
        
        # Unlike
        response = self.client.post(url)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['total_likes'], 0)


class AdminAPITest(TestCase):
    """Tests for Admin API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.admin_profile = UserProfile.objects.create(user=self.admin, is_admin=True)
        refresh = RefreshToken.for_user(self.admin)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_admin_stats_api(self):
        """Test admin statistics endpoint"""
        url = reverse('api-admin-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('total_posts', response.data)
        self.assertIn('total_comments', response.data)
    
    def test_admin_users_api(self):
        """Test admin users list endpoint"""
        url = reverse('api-admin-users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class UnauthenticatedAPITest(TestCase):
    """Tests for API access without authentication"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            body='Test body',
            author=self.user
        )
    
    def test_unauthenticated_post_list(self):
        """Test accessing post list without authentication"""
        url = reverse('api-post-list')
        response = self.client.get(url)
        # Should allow read access
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_post_create(self):
        """Test creating post without authentication"""
        url = reverse('api-post-list')
        data = {'title': 'Test', 'body': 'Content'}
        response = self.client.post(url, data, format='json')
        # Should deny write access
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



