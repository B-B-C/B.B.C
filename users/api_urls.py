from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from . import api_views

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/custom/', api_views.token_refresh_api, name='api-token-refresh-custom'),
    
    # Custom authentication endpoints
    path('register/', api_views.register_api, name='api-register'),
    path('login/', api_views.login_api, name='api-login'),
    path('logout/', api_views.logout_api, name='api-logout'),
    
    # User profile endpoints
    path('profile/', api_views.profile_api, name='api-profile'),
    path('profile/update/', api_views.update_profile_api, name='api-profile-update'),
    
    # Admin endpoints
    path('admin/users/', api_views.admin_users_api, name='api-admin-users'),
]