from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Message, Report
import re

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password1):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("Password must contain at least one special character.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Tell us about yourself'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'userprofile'):
            self.fields['bio'].initial = self.instance.userprofile.bio
            self.fields['avatar'].initial = self.instance.userprofile.avatar

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        return current_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', new_password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', new_password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', new_password1):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password1):
            raise ValidationError("Password must contain at least one special character.")
        return new_password1

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("New passwords don't match.")
        
        return cleaned_data


class MessageForm(forms.ModelForm):
    recipient_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        }),
        label='Получатель'
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите ваше сообщение...'
        }),
        label='Сообщение'
    )
    
    class Meta:
        model = Message
        fields = ['content']
    
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
    
    def clean_recipient_username(self):
        username = self.cleaned_data.get('recipient_username')
        if not username:
            raise ValidationError("Введите имя пользователя.")
        
        try:
            recipient = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("Пользователь с таким именем не найден.")
        
        if self.sender and recipient == self.sender:
            raise ValidationError("Вы не можете отправить сообщение самому себе.")
        
        return recipient
    
    def save(self, commit=True):
        message = super().save(commit=False)
        message.sender = self.sender
        message.recipient = self.cleaned_data['recipient_username']
        if commit:
            message.save()
        return message


class ReportForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Опишите проблему подробно...'
        }),
        label='Описание проблемы',
        required=True
    )
    reason = forms.ChoiceField(
        choices=Report.REPORT_REASONS,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Причина жалобы',
        required=True
    )
    
    class Meta:
        model = Report
        fields = ['reason', 'description']
    
    def __init__(self, *args, **kwargs):
        self.reporter = kwargs.pop('reporter', None)
        self.report_type = kwargs.pop('report_type', None)
        self.reported_post = kwargs.pop('reported_post', None)
        self.reported_comment = kwargs.pop('reported_comment', None)
        self.reported_user = kwargs.pop('reported_user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Проверяем, что указан хотя бы один объект для жалобы
        if not self.reported_post and not self.reported_comment and not self.reported_user:
            raise ValidationError("Необходимо указать объект для жалобы.")
        
        # Проверяем, что пользователь не жалуется сам на себя
        if self.reported_user and self.reporter and self.reported_user == self.reporter:
            raise ValidationError("Вы не можете пожаловаться на самого себя.")
        
        return cleaned_data
    
    def save(self, commit=True):
        report = super().save(commit=False)
        report.reporter = self.reporter
        report.report_type = self.report_type
        
        if self.reported_post:
            report.reported_post = self.reported_post
        elif self.reported_comment:
            report.reported_comment = self.reported_comment
        elif self.reported_user:
            report.reported_user = self.reported_user
        
        if commit:
            report.save()
        return report
