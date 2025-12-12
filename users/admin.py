from django.contrib import admin
from .models import UserProfile, Message, Report

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_admin', 'is_banned', 'created_at']
    list_filter = ['is_admin', 'is_banned', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'content_preview', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Содержание'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'report_type', 'reporter', 'reason', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status', 'report_type', 'reason', 'created_at']
    search_fields = ['reporter__username', 'description', 'admin_notes']
    readonly_fields = ['created_at', 'reviewed_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('reporter', 'report_type', 'reason', 'status')
        }),
        ('Объект жалобы', {
            'fields': ('reported_post', 'reported_comment', 'reported_user')
        }),
        ('Детали', {
            'fields': ('description', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Даты', {
            'fields': ('created_at',)
        }),
    )
