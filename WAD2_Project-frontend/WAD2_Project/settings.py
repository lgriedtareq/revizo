import os

# Build paths inside the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

# Security settings
SECRET_KEY = 'niq41t%!1vr+w@g-6g+(^2!uxfal&(95h8$@y^xv@=pb%2n1te'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']  # ✅ Fixed allowed hosts

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'revizo',
    'corsheaders',  #  Added CORS for API communication
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Enable CORS for API communication
CORS_ALLOW_ALL_ORIGINS = True  #  Allows frontend to access backend API

# URL configurations
ROOT_URLCONF = 'WAD2_Project.urls'  #  Ensure this matches your project
WSGI_APPLICATION = 'WAD2_Project.wsgi.application'  #  Correct


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Media files
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'

# Static files
STATIC_URL = '/static/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # Ensure static folder is properly referenced
]

# Collect static files in one place (useful for deployment)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ✅ Fixed login redirect
LOGIN_URL = 'revizo:login'  # ✅ Ensure this matches your app's login URL

# ✅ Fix default primary key type warning
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
