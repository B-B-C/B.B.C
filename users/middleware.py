from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import UserProfile


class BanCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and banned
        if request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                if profile.is_banned:
                    # Check if ban has expired
                    if profile.banned_until and profile.banned_until <= timezone.now():
                        # Ban has expired, unban the user
                        profile.is_banned = False
                        profile.ban_reason = None
                        profile.banned_until = None
                        profile.save()
                    else:
                        # User is still banned
                        if not request.path.startswith('/users/logout/'):
                            messages.error(request, f'Вы забанены. Причина: {profile.ban_reason or "Не указана"}')
                            return redirect('forum-index')
            except UserProfile.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
