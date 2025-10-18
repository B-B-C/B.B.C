# Инструкция по установке

## Системные требования

- Python 3.11+
- PostgreSQL 15+ (для продакшена)
- Docker и Docker Compose (опционально)
- Git

## Локальная установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd lummel-master
```

### 2. Создание виртуального окружения

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

#### SQLite (для разработки)
```bash
python manage.py migrate
```

#### PostgreSQL (для продакшена)
1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE forum_db;
CREATE USER forum_user WITH PASSWORD 'forum_password';
GRANT ALL PRIVILEGES ON DATABASE forum_db TO forum_user;
```

3. Настройте переменные окружения:
```bash
export DATABASE_URL=postgres://forum_user:forum_password@localhost:5432/forum_db
```

4. Выполните миграции:
```bash
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 6. Сбор статических файлов

```bash
python manage.py collectstatic
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://localhost:8000

## Docker установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd lummel-master
```

### 2. Запуск с Docker Compose

```bash
docker-compose up --build
```

### 3. Выполнение миграций

```bash
docker-compose exec web python manage.py migrate
```

### 4. Создание суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

## Настройка мониторинга

### 1. Запуск Prometheus и Grafana

```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Доступ к сервисам

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Нагрузочное тестирование

### 1. Установка k6

#### Windows (Chocolatey)
```bash
choco install k6
```

#### Linux
```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

#### Mac (Homebrew)
```bash
brew install k6
```

### 2. Запуск тестов

```bash
k6 run load-testing/load-test.js
```

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/database
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Настройка для продакшена

### 1. Переменные окружения

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgres://user:password@host:port/database
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Настройка статических файлов

```bash
python manage.py collectstatic --noinput
```

### 3. Настройка веб-сервера (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## Разработка

### 1. Установка зависимостей для разработки

```bash
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov black flake8
```

### 2. Запуск тестов

```bash
python manage.py test
# или
pytest
```

### 3. Проверка кода

```bash
black .
flake8 .
```

### 4. Запуск с отладкой

```bash
python manage.py runserver --settings=forum_project.settings
```

## Устранение неполадок

### Проблема: Ошибка подключения к базе данных

**Решение:**
1. Проверьте, что PostgreSQL запущен
2. Проверьте правильность DATABASE_URL
3. Убедитесь, что база данных существует

### Проблема: Ошибка статических файлов

**Решение:**
```bash
python manage.py collectstatic --noinput
```

### Проблема: Ошибка миграций

**Решение:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Проблема: Ошибка разрешений

**Решение:**
```bash
chmod +x manage.py
```

## Поддержка

При возникновении проблем:

1. Проверьте логи: `tail -f logs/django.log`
2. Создайте Issue в репозитории
3. Обратитесь к документации Django

