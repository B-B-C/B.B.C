from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """API для регистрации пользователя с JWT токенами"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not all([username, email, password]):
        return Response({
            'error': 'All fields are required',
            'detail': 'Username, email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists',
            'detail': 'A user with this username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'Email already exists',
            'detail': 'A user with this email already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    UserProfile.objects.create(user=user)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """API для входа пользователя с JWT токенами"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not all([username, password]):
        return Response({
            'error': 'Username and password are required',
            'detail': 'Both username and password fields are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        # Check if user is banned
        try:
            profile = user.userprofile
            if profile.is_banned:
                from django.utils import timezone
                if profile.banned_until and profile.banned_until > timezone.now():
                    return Response({
                        'error': 'Account banned',
                        'detail': f'Account is banned until {profile.banned_until}. Reason: {profile.ban_reason or "Not specified"}'
                    }, status=status.HTTP_403_FORBIDDEN)
                elif not profile.banned_until:
                    return Response({
                        'error': 'Account permanently banned',
                        'detail': f'Account is permanently banned. Reason: {profile.ban_reason or "Not specified"}'
                    }, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            pass
        
        if not user.is_active:
            return Response({
                'error': 'Account inactive',
                'detail': 'This account has been deactivated'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    else:
        return Response({
            'error': 'Invalid credentials',
            'detail': 'Unable to log in with provided credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """API для выхода пользователя (blacklist refresh token)"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        else:
            return Response({
                'error': 'Refresh token required',
                'detail': 'Refresh token is required in request body'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Invalid token',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh_api(request):
    """API для обновления access token"""
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({
            'error': 'Refresh token required',
            'detail': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token)
        })
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token',
            'detail': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_api(request):
    """API для получения профиля пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    """API для обновления профиля пользователя"""
    user = request.user
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    user.save()
    
    return Response(UserSerializer(user).data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_api(request):
    """API для получения списка пользователей (только для админов)"""
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)