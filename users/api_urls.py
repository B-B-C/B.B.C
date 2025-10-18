from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from . import api_views

urlpatterns = [
    path('token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', api_views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('register/', api_views.register_api, name='register_api'),
    path('profile/', api_views.user_profile_api, name='user_profile_api'),
    path('profile/update/', api_views.update_profile_api, name='update_profile_api'),
    path('logout/', api_views.logout_api, name='logout_api'),
]

