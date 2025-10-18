from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, null=True, help_text="Причина бана")
    banned_until = models.DateTimeField(blank=True, null=True, help_text="Бан до (оставьте пустым для постоянного бана)")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"
