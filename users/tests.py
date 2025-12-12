from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile
from .forms import UserRegisterForm, UserProfileForm
import json


class UserModelTest(TestCase):
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
            is_admin=False,
            is_banned=False
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertFalse(profile.is_admin)
        self.assertFalse(profile.is_banned)
        
    def test_user_profile_string_representation(self):
        """Тест строкового представления профиля"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), 'testuser Profile')
        
    def test_user_profile_with_avatar(self):
        """Тест профиля с аватаром"""
        avatar = SimpleUploadedFile(
            "avatar.jpg",
            b"fake_avatar_content",
            content_type="image/jpeg"
        )
        
        profile = UserProfile.objects.create(
            user=self.user,
            avatar=avatar
        )
        
        self.assertTrue(profile.avatar)
        
    def test_banned_user_profile(self):
        """Тест забаненного пользователя"""
        profile = UserProfile.objects.create(
            user=self.user,
            is_banned=True,
            ban_reason='Spam',
            banned_until=None  # Permanent ban
        )
        
        self.assertTrue(profile.is_banned)
        self.assertEqual(profile.ban_reason, 'Spam')
        self.assertIsNone(profile.banned_until)


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        
    def test_register_view(self):
        """Тест регистрации пользователя"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Регистрация')
        
    def test_user_registration(self):
        """Тест процесса регистрации"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
    def test_login_view(self):
        """Тест страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход')
        
    def test_user_login(self):
        """Тест процесса входа"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertRedirects(response, reverse('forum-index'))
        
    def test_profile_view_authenticated(self):
        """Тест страницы профиля авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        
    def test_profile_view_anonymous(self):
        """Тест страницы профиля неавторизованного пользователя"""
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/users/login/?next=/users/profile/')
        
    def test_edit_profile_view(self):
        """Тест редактирования профиля"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        
    def test_profile_update(self):
        """Тест обновления профиля"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('edit_profile'), {
            'bio': 'Updated bio',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        
    def test_password_change_view(self):
        """Тест смены пароля"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
        
    def test_password_change(self):
        """Тест процесса смены пароля"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('password_change'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        
        self.assertRedirects(response, reverse('password_change_done'))
        
        # Проверяем, что старый пароль больше не работает
        self.client.logout()
        login_response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertContains(login_response, 'Пожалуйста, введите правильные имя пользователя и пароль')
        
        # Проверяем, что новый пароль работает
        login_response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'newpass123'
        })
        self.assertRedirects(login_response, reverse('forum-index'))


class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Обычный пользователь
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        
        # Админ
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
        self.assertContains(response, 'Панель администратора')
        
    def test_admin_users_view(self):
        """Тест страницы управления пользователями"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_users'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'admin')
        
    def test_admin_user_detail_view(self):
        """Тест страницы детальной информации о пользователе"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_user_detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        
    def test_toggle_user_status(self):
        """Тест переключения статуса пользователя"""
        self.client.login(username='admin', password='adminpass123')
        
        # Деактивируем пользователя
        response = self.client.post(reverse('admin_toggle_user_status', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # Активируем обратно
        response = self.client.post(reverse('admin_toggle_user_status', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
    def test_toggle_admin_status(self):
        """Тест переключения админ статуса"""
        self.client.login(username='admin', password='adminpass123')
        
        # Назначаем админом
        response = self.client.post(reverse('admin_toggle_admin_status', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_admin)
        
        # Снимаем админа
        response = self.client.post(reverse('admin_toggle_admin_status', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_admin)
        
    def test_ban_user(self):
        """Тест бана пользователя"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(
            reverse('admin_ban_user', args=[self.user.id]),
            json.dumps({
                'ban_reason': 'Spam',
                'ban_duration': '7'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_banned)
        self.assertEqual(self.profile.ban_reason, 'Spam')
        
    def test_unban_user(self):
        """Тест разбана пользователя"""
        # Сначала баним
        self.profile.is_banned = True
        self.profile.ban_reason = 'Spam'
        self.profile.save()
        
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(reverse('admin_unban_user', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_banned)
        self.assertIsNone(self.profile.ban_reason)


class FormsTest(TestCase):
    def test_user_register_form(self):
        """Тест формы регистрации"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_register_form_password_mismatch(self):
        """Тест формы регистрации с несовпадающими паролями"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_user_profile_form(self):
        """Тест формы профиля"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'bio': 'Test bio',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = UserProfileForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())