# API Документация

## Базовый URL
```
http://localhost:8000/api/
```

## Аутентификация

### Session Authentication
Используется для веб-интерфейса. Пользователь должен быть залогинен через веб-форму.

### Token Authentication
Для мобильных приложений и внешних API.

#### Получение токена
```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

#### Использование токена
```http
Authorization: Token your_token_here
```

## Эндпоинты

### Посты

#### Получить список постов
```http
GET /api/posts/
```

**Параметры запроса:**
- `page` - номер страницы (по умолчанию 1)
- `search` - поиск по заголовку и содержанию
- `author` - фильтр по автору
- `ordering` - сортировка (created_at, -created_at, title, -title)

**Пример ответа:**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/posts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Заголовок поста",
            "body": "Содержание поста",
            "author": 1,
            "author_username": "username",
            "created_at": "2024-01-01T12:00:00Z",
            "likes_count": 5,
            "comments_count": 3,
            "is_liked": false
        }
    ]
}
```

#### Создать пост
```http
POST /api/posts/
Authorization: Token your_token_here
Content-Type: application/json

{
    "title": "Заголовок поста",
    "body": "Содержание поста"
}
```

#### Получить пост
```http
GET /api/posts/{id}/
```

#### Обновить пост
```http
PUT /api/posts/{id}/
Authorization: Token your_token_here
Content-Type: application/json

{
    "title": "Новый заголовок",
    "body": "Новое содержание"
}
```

#### Удалить пост
```http
DELETE /api/posts/{id}/
Authorization: Token your_token_here
```

### Комментарии

#### Получить комментарии к посту
```http
GET /api/posts/{post_id}/comments/
```

#### Создать комментарий
```http
POST /api/posts/{post_id}/comments/
Authorization: Token your_token_here
Content-Type: application/json

{
    "content": "Текст комментария"
}
```

### Лайки

#### Лайк/анлайк поста
```http
POST /api/posts/{post_id}/like/
Authorization: Token your_token_here
```

**Ответ:**
```json
{
    "liked": true,
    "total_likes": 6
}
```

### Поиск

#### Поиск постов
```http
GET /api/search/?q=поисковый_запрос
```

**Параметры:**
- `q` - поисковый запрос (обязательный)

## Коды ответов

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `400 Bad Request` - Неверный запрос
- `401 Unauthorized` - Не авторизован
- `403 Forbidden` - Доступ запрещен
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Внутренняя ошибка сервера

## Ограничения

- Максимальная длина заголовка поста: 200 символов
- Максимальная длина содержания поста: 10000 символов
- Максимальная длина комментария: 1000 символов
- Пагинация: 20 элементов на страницу

## Примеры использования

### JavaScript (Fetch API)
```javascript
// Получение списка постов
fetch('/api/posts/')
    .then(response => response.json())
    .then(data => console.log(data));

// Создание поста
fetch('/api/posts/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token your_token_here'
    },
    body: JSON.stringify({
        title: 'Новый пост',
        body: 'Содержание поста'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python (requests)
```python
import requests

# Получение списка постов
response = requests.get('http://localhost:8000/api/posts/')
posts = response.json()

# Создание поста
headers = {'Authorization': 'Token your_token_here'}
data = {
    'title': 'Новый пост',
    'body': 'Содержание поста'
}
response = requests.post('http://localhost:8000/api/posts/', 
                        headers=headers, json=data)
```

### cURL
```bash
# Получение списка постов
curl -X GET http://localhost:8000/api/posts/

# Создание поста
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{"title": "Новый пост", "body": "Содержание поста"}'
```

