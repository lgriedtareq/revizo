# Revizo - Flashcard Learning Platform
lgriedtareq.pythonanywhere.com

1. Clone the repository:
```bash
git clone [repository-url]
cd WAD2_Project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your API keys:
```
ANTHROPIC_API_KEY=your_api_key_here
SECRET_KEY=your_django_secret_key_here
```

5. Set up the database:
```bash
python manage.py migrate
```

6. Populate the database with sample data:
```bash
python population_script.py
```

7. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

9. Visit http://127.0.0.1:8000/ in your browser

## Features
- User registration and authentication
- Flashcard creation and management
- AI-powered explanations and suggestions
- Spaced repetition learning system
- Dark mode support

## External Sources & Acknowledgments

### APIs & Services
- Anthropic Claude API - For AI-powered flashcard explanations
- Bootstrap 5 - Frontend framework for responsive design

### JavaScript Libraries
- jQuery - JavaScript library for DOM manipulation
- Popper.js - For tooltips and popovers
- Font Awesome - For icons and visual elements

### Python Packages
- Django 3.2.25 - Web framework
- python-dotenv - Environment variable management
- anthropic - Anthropic Claude API SDK
- django-cors-headers - Cross-Origin Resource Sharing
- djangorestframework - REST API framework
- Pillow - Image processing
- django-filter - Dynamic queryset filtering
- django-crispy-forms - Form rendering
- crispy-bootstrap4 - Bootstrap 4 template pack

