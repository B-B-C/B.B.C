from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, Comment
from users.models import UserProfile
import tempfile
import os


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        
    def test_post_creation(self):
        """Тест создания поста"""
        post = Post.objects.create(
            title='Test Post',
            body='This is a test post',
            author=self.user
        )
        self.assertEqual(str(post), 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertIsNotNone(post.created_at)
        
    def test_post_with_image(self):
        """Тест создания поста с изображением"""
        # Создаем временный файл изображения
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        
        post = Post.objects.create(
            title='Test Post with Image',
            body='This post has an image',
            author=self.user,
            image=image
        )
        
        self.assertTrue(post.image)
        self.assertEqual(post.title, 'Test Post with Image')


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.post = Post.objects.create(
            title='Test Post',
            body='This is a test post',
            author=self.user
        )
        
    def test_comment_creation(self):
        """Тест создания комментария"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment'
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, 'This is a test comment')
        
    def test_comment_with_sticker(self):
        """Тест создания комментария со стикером"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Great post!',
            sticker='😀'
        )
        self.assertEqual(comment.sticker, '😀')
        
    def test_comment_with_image(self):
        """Тест создания комментария с изображением"""
        image = SimpleUploadedFile(
            "comment_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Check this out!',
            image=image
        )
        
        self.assertTrue(comment.image)


class ForumViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.post = Post.objects.create(
            title='Test Post',
            body='This is a test post',
            author=self.user
        )
        
    def test_index_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('forum-index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Темы форума')
        
    def test_index_view_with_sorting(self):
        """Тест сортировки на главной странице"""
        # Создаем еще один пост
        Post.objects.create(
            title='Another Post',
            body='Another test post',
            author=self.user
        )
        
        response = self.client.get(reverse('forum-index') + '?sort=oldest')
        self.assertEqual(response.status_code, 200)
        
    def test_index_view_with_search(self):
        """Тест поиска на главной странице"""
        response = self.client.get(reverse('forum-index') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        
    def test_thread_detail_view(self):
        """Тест страницы поста"""
        response = self.client.get(reverse('thread-detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        
    def test_new_post_view_authenticated(self):
        """Тест создания поста авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('new-post'))
        self.assertEqual(response.status_code, 200)
        
    def test_new_post_view_anonymous(self):
        """Тест создания поста неавторизованным пользователем"""
        response = self.client.get(reverse('new-post'))
        self.assertRedirects(response, '/users/login/?next=/new-post/')
        
    def test_post_creation(self):
        """Тест создания поста через форму"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('new-post'), {
            'title': 'New Test Post',
            'body': 'This is a new test post'
        })
        
        self.assertRedirects(response, reverse('thread-detail', args=[2]))
        self.assertTrue(Post.objects.filter(title='New Test Post').exists())
        
    def test_comment_creation(self):
        """Тест создания комментария"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('thread-detail', args=[self.post.id]), {
            'content': 'This is a test comment'
        })
        
        self.assertRedirects(response, reverse('thread-detail', args=[self.post.id]))
        self.assertTrue(Comment.objects.filter(content='This is a test comment').exists())
        
    def test_comment_with_sticker(self):
        """Тест создания комментария со стикером"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('thread-detail', args=[self.post.id]), {
            'content': 'Great post!',
            'sticker': '😀'
        })
        
        self.assertRedirects(response, reverse('thread-detail', args=[self.post.id]))
        comment = Comment.objects.get(content='Great post!')
        self.assertEqual(comment.sticker, '😀')
        
    def test_like_toggle(self):
        """Тест лайка поста"""
        self.client.login(username='testuser', password='testpass123')
        
        # Лайк поста
        response = self.client.post(reverse('toggle-like', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user in self.post.likes.all())
        
        # Убираем лайк
        response = self.client.post(reverse('toggle-like', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user in self.post.likes.all())


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_user_profile_creation(self):
        """Тест создания профиля пользователя"""
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            is_admin=False
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertFalse(profile.is_admin)
        self.assertFalse(profile.is_banned)
        
    def test_user_profile_string_representation(self):
        """Тест строкового представления профиля"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), 'testuser Profile')


class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        
        # Создаем админа
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin,
            is_admin=True
        )
        
    def test_admin_dashboard_access(self):
        """Тест доступа к админ панели"""
        # Обычный пользователь
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)
        
        # Админ
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_admin_users_view(self):
        """Тест страницы управления пользователями"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_users'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        
    def test_admin_posts_view(self):
        """Тест страницы управления постами"""
        # Создаем пост
        Post.objects.create(
            title='Test Post',
            body='Test content',
            author=self.user
        )
        
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_posts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')