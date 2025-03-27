from django.urls import path
from revizo import views

app_name = 'revizo'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('flashcards/', views.flashcards, name='flashcards'),
    path('flashcards/create/', views.create_flashcard, name='create_flashcard'),
    path('flashcards/create/subject/', views.create_subject, name='create_subject'),
    path('flashcards/create/topic/', views.create_topic, name='create_topic'),
    path('flashcards/organize/', views.create_organization, name='create_organization'),
    path('flashcards/add/', views.add_flashcard, name='add_flashcard'),
    path('flashcards/filter/', views.filter_flashcards, name='filter_flashcards'),
    path('flashcards/delete/<int:pk>/', views.delete_flashcard, name='delete_flashcard'),
    path('flashcards/edit/<int:pk>/', views.edit_flashcard, name='edit_flashcard'),
    path('get-topics/', views.get_topics, name='get_topics'),
    path('study/', views.study, name='study'),
    
    # API endpoints
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('update-confidence/<int:pk>/', views.update_confidence, name='update_confidence'),
    path('get-ai-explanation/<int:card_id>/', views.get_ai_explanation, name='get_ai_explanation'),
    path('flashcards/explanation/', views.get_card_explanation, name='get_card_explanation'),
    path('flashcards/suggestions/', views.get_related_cards, name='get_related_cards'),
]
