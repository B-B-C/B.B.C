"""
API Tests for Users App
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile


class UserAPITest(TestCase):
    """Tests for User API endpoints"""
    
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
    
    def test_profile_api(self):
        """Test getting user profile"""
        url = reverse('api-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_profile_api(self):
        """Test updating user profile"""
        url = reverse('api-profile-update')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newemail@example.com'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'newemail@example.com')
    
    def test_register_api_validation(self):
        """Test registration API with invalid data"""
        url = reverse('api-register')
        
        # Test missing fields
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test duplicate username
        data = {
            'username': 'testuser',
            'email': 'new@example.com',
            'password': 'pass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_banned_user(self):
        """Test login for banned user"""
        self.profile.is_banned = True
        self.profile.ban_reason = 'Spam'
        self.profile.save()
        
        url = reverse('api-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('banned', response.data['error'].lower())


class AdminAPITest(TestCase):
    """Tests for Admin API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        
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
    
    def test_admin_users_api(self):
        """Test admin users list endpoint"""
        url = reverse('api-admin-users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 2)  # At least admin and testuser
    
    def test_admin_users_api_unauthorized(self):
        """Test admin users API access without admin privileges"""
        # Use regular user token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
        url = reverse('api-admin-users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



