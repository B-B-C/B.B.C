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


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"От {self.sender.username} к {self.recipient.username}: {self.content[:50]}"


class Report(models.Model):
    REPORT_TYPES = [
        ('post', 'Пост'),
        ('comment', 'Комментарий'),
        ('user', 'Пользователь'),
    ]
    
    REPORT_REASONS = [
        ('spam', 'Спам'),
        ('harassment', 'Оскорбления/Харассмент'),
        ('inappropriate', 'Неуместный контент'),
        ('copyright', 'Нарушение авторских прав'),
        ('other', 'Другое'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('reviewed', 'Рассмотрено'),
        ('resolved', 'Решено'),
        ('dismissed', 'Отклонено'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(help_text="Подробное описание проблемы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Связи с объектами жалобы
    reported_post = models.ForeignKey('forum.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reported_comment = models.ForeignKey('forum.Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_against')
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    admin_notes = models.TextField(blank=True, null=True, help_text="Заметки администратора")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.reported_post:
            return f"Жалоба на пост от {self.reporter.username}"
        elif self.reported_comment:
            return f"Жалоба на комментарий от {self.reporter.username}"
        elif self.reported_user:
            return f"Жалоба на пользователя {self.reported_user.username} от {self.reporter.username}"
        return f"Жалоба от {self.reporter.username}"
