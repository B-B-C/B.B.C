from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post, Comment
from users.models import UserProfile

class ForumModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            is_admin=False
        )

    def test_post_creation(self):
        post = Post.objects.create(
            title='Test Post',
            body='This is a test post',
            author=self.user
        )
        self.assertEqual(str(post), 'Test Post')
        self.assertEqual(post.author, self.user)

    def test_comment_creation(self):
        post = Post.objects.create(
            title='Test Post',
            body='This is a test post',
            author=self.user
        )
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            content='This is a test comment'
        )
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.author, self.user)

class ForumAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            is_admin=False
        )
        self.post = Post.objects.create(
            title='Test Post',
            body='This is a test post',
            author=self.user
        )

    def test_post_list_api(self):
        url = reverse('api-post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_post_creation_api(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api-post-list')
        data = {
            'title': 'New Post',
            'body': 'This is a new post'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_like_api(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api-toggle-like', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['total_likes'], 1)

    def test_search_api(self):
        url = reverse('api-search')
        response = self.client.get(url, {'q': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class ForumViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            is_admin=False
        )

    def test_index_view(self):
        response = self.client.get(reverse('forum-index'))
        self.assertEqual(response.status_code, 200)

    def test_new_post_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('new-post'))
        self.assertEqual(response.status_code, 200)

    def test_new_post_view_unauthenticated(self):
        response = self.client.get(reverse('new-post'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_post_creation(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'Test Post',
            'body': 'This is a test post'
        }
        response = self.client.post(reverse('new-post'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertEqual(Post.objects.count(), 1)
