# B.B.C Forum - Enhanced Django Project

A modern, secure Django forum application with comprehensive user management, JWT authentication, and admin dashboard.

## 🚀 Features

### Security
- **Password Hashing**: Argon2, PBKDF2, and BCrypt password hashers
- **CSRF Protection**: Comprehensive CSRF protection with secure cookies
- **XSS Protection**: Browser XSS filter and content type sniffing protection
- **HSTS**: HTTP Strict Transport Security with preload support
- **Secure Cookies**: HttpOnly, Secure, and SameSite cookie attributes
- **JWT Authentication**: Secure token-based authentication

### User Management
- **Registration Validation**: Server-side and client-side validation
  - Email format validation
  - Password strength requirements (8+ chars, uppercase, lowercase, numbers, special characters)
  - Username uniqueness and format validation
  - Password confirmation matching
- **Profile Management**: 
  - Avatar upload functionality
  - Bio and personal information editing
  - Password change with current password verification
- **Personal Dashboard**: User activity history and statistics

### Admin Features
- **Custom Admin Dashboard**: Accessible from main site (not Django default)
- **User Management**: View, edit, activate/deactivate users
- **Content Management**: Manage posts and comments
- **Admin Privileges**: Grant/revoke admin status
- **Statistics**: Comprehensive site statistics

### API Features
- **JWT Endpoints**: `/api/auth/token/` and `/api/auth/token/refresh/`
- **User Registration API**: `/api/auth/register/`
- **Profile Management API**: `/api/auth/profile/`
- **RESTful Design**: Full REST API with proper HTTP methods

### Database & Documentation
- **ER Diagram**: Database structure visualization
- **Model Documentation**: Comprehensive model relationships
- **Migration Support**: Backward-compatible database updates

### UI/UX
- **Modern Dark Theme**: Bootstrap 5 with dark mode support
- **Responsive Design**: Mobile-first responsive layout
- **Crispy Forms**: Enhanced form styling with Bootstrap 5
- **Avatar Support**: Image upload and display functionality

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
   cd B.B.C-main
```

2. **Create virtual environment**
```bash
python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Database setup**
```bash
   python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Create media directories**
   ```bash
   mkdir media
   mkdir media/avatars
   ```

8. **Run development server**
```bash
python manage.py runserver
```

## 📁 Project Structure

```
B.B.C-main/
├── forum/                    # Main forum application
│   ├── models.py            # Post and Comment models
│   ├── views.py             # Forum views
│   ├── templates/           # Forum templates
│   └── api_views.py         # Forum API endpoints
├── users/                   # User management application
│   ├── models.py            # UserProfile model
│   ├── views.py             # User views
│   ├── admin_views.py       # Custom admin views
│   ├── forms.py             # Enhanced forms with validation
│   ├── serializers.py       # API serializers
│   └── templates/           # User templates
├── forum_project/           # Django project settings
│   ├── settings.py          # Enhanced security settings
│   └── urls.py              # URL configuration
├── media/                   # User uploaded files
│   └── avatars/             # User avatars
├── static/                  # Static files
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration

### Security Settings
The project includes comprehensive security settings in `settings.py`:

- **Password Hashing**: Multiple hashers for security
- **CSRF Protection**: Secure cookie settings
- **XSS Protection**: Browser security headers
- **HSTS**: Transport security
- **Cookie Security**: HttpOnly, Secure, SameSite attributes

### JWT Configuration
JWT tokens are configured with:
- **Access Token**: 60 minutes lifetime
- **Refresh Token**: 7 days lifetime
- **Token Rotation**: Automatic refresh token rotation
- **Blacklisting**: Token blacklisting on logout

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/blacklist/` - Blacklist refresh token

### User Management
- `POST /api/auth/register/` - User registration
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile
- `POST /api/auth/logout/` - Logout user

## 🎨 UI Components

### Templates
- **Base Template**: Dark theme with Bootstrap 5
- **Registration Form**: Enhanced validation and styling
- **Profile Pages**: Modern user interface
- **Admin Dashboard**: Comprehensive admin interface
- **Responsive Design**: Mobile-first approach

### Forms
- **User Registration**: Server-side and client-side validation
- **Profile Editing**: Avatar upload and bio editing
- **Password Change**: Secure password update
- **Crispy Forms**: Bootstrap 5 integration

## 🔒 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### CSRF Protection
- CSRF tokens on all forms
- Secure cookie settings
- Trusted origins configuration

### XSS Protection
- Browser XSS filter
- Content type sniffing protection
- Secure headers configuration

## 📊 Admin Dashboard

### Features
- **User Management**: View, edit, activate/deactivate users
- **Content Management**: Manage posts and comments
- **Statistics**: Site-wide statistics
- **Admin Controls**: Grant/revoke admin privileges

### Access
- Navigate to `/users/admin/dashboard/`
- Requires admin privileges
- Custom interface (not Django default admin)

## 🗄️ Database

### Models
- **User**: Extended with UserProfile
- **Post**: Forum posts with likes
- **Comment**: Post comments
- **UserProfile**: User bio, avatar, admin status

### ER Diagram
Generate database diagram:
```bash
python manage.py graph_models -a -o er_diagram.png
```

## 🚀 Deployment

### Production Settings
- Set `DEBUG=False`
- Configure `SECRET_KEY`
- Set up database (PostgreSQL recommended)
- Configure static file serving
- Set up media file serving

### Environment Variables
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_HOSTS=your-domain.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔄 Updates

### Recent Updates
- Enhanced security settings
- JWT authentication implementation
- Custom admin dashboard
- User profile management
- Avatar upload functionality
- Modern UI with Bootstrap 5
- Comprehensive validation
- API endpoints for mobile apps

### Future Enhancements
- Real-time notifications
- Advanced search functionality
- Email notifications
- Social login integration
- Advanced admin analytics