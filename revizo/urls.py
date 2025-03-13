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
    path("flashcards/add/", views.add_flashcard, name="add_flashcard"),
    path("flashcards/edit/<int:pk>", views.edit_flashcard, name="edit_flashcard"),
    path("flashcards/delete/<int:pk>", views.delete_flashcard, name="delete_flashcard"),
    path("flashcards/filter/", views.filter_flashcards, name="filter_flashcards"),
    path('get_topics/', views.get_topics, name='get_topics'),
    path('study/', views.study, name='study'),
    path('contact', views.contact_us, name='contact_us'),
]

""" building basis,  rememeber to add other links such as contact """