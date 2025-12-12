# Django Forum - Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Docker Development
```bash
# Start with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 🌐 Production Deployment

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Add environment variables:
   - `SECRET_KEY`: Your Django secret key
   - `DATABASE_URL`: PostgreSQL connection string
   - `DEBUG`: Set to `False`
3. Deploy automatically on push to main branch

### Heroku Deployment
1. Install Heroku CLI
2. Create Heroku app:
   ```bash
   heroku create your-forum-app
   ```
3. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
4. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   ```
5. Deploy:
   ```bash
   git push heroku main
   ```

### DigitalOcean App Platform
1. Connect your GitHub repository
2. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn forum_project.wsgi:application`
3. Add environment variables
4. Deploy

## 📊 Monitoring Setup

### Start Monitoring Stack
```bash
# Start with monitoring
./start_monitoring.sh

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Access Monitoring Tools
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Alertmanager**: http://localhost:9093

### Grafana Dashboard
Import the Django Forum dashboard from `monitoring/grafana/dashboards/django_forum.json`

## 🧪 Testing

### Run Unit Tests
```bash
python manage.py test
```

### Run with Coverage
```bash
pip install pytest pytest-cov
pytest --cov=. --cov-report=html
```

### Load Testing
```bash
# Install k6
# Linux: https://k6.io/docs/getting-started/installation/
# macOS: brew install k6

# Run load tests
k6 run load_tests/forum_load_test.js
```

## 🔧 Environment Variables

### Required
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `DATABASE_URL`: PostgreSQL connection string

### Optional
- `USE_SQLITE`: Use SQLite for development
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_HOST`: Database host
- `POSTGRES_PORT`: Database port

## 📁 Project Structure

```
forum_project/
├── forum/                 # Forum app
├── users/                 # Users app
├── forum_project/        # Django project settings
├── static/               # Static files
├── media/                # Media files
├── monitoring/           # Monitoring configuration
├── load_tests/           # Load testing scripts
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker image
└── requirements.txt     # Python dependencies
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL is running
   - Verify credentials

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT setting
   - Verify web server configuration

3. **Media Files Not Loading**
   - Check MEDIA_ROOT and MEDIA_URL settings
   - Verify file permissions
   - Check web server configuration

4. **Docker Issues**
   - Check Docker and Docker Compose versions
   - Ensure ports are not in use
   - Check container logs: `docker-compose logs`

### Performance Optimization

1. **Database Optimization**
   - Add database indexes
   - Use connection pooling
   - Enable query caching

2. **Static Files**
   - Use CDN for static files
   - Enable gzip compression
   - Set proper cache headers

3. **Application**
   - Use Redis for caching
   - Enable database query optimization
   - Use async views where possible

## 📞 Support

For issues and questions:
- Check the logs: `docker-compose logs web`
- Review monitoring dashboards
- Check GitHub Issues




