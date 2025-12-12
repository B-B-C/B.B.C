from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image', 'video']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок темы'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите вашу тему...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image', 'sticker']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий... (необязательно)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'sticker': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите стикер или введите эмодзи...',
                'id': 'sticker-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '') or ''
        image = cleaned_data.get('image')
        sticker = cleaned_data.get('sticker', '') or ''
        
        # Очищаем от пробелов
        content = content.strip()
        sticker = sticker.strip()
        
        # Если нет ни текста, ни изображения, ни стикера - ошибка
        if not content and not image and not sticker:
            raise forms.ValidationError('Добавьте текст, изображение или стикер к комментарию.')
        
        return cleaned_data
