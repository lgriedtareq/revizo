from django.urls import path
from .views import get_data, some_view  #  Import necessary views

urlpatterns = [
    path('', some_view, name='home'),  #  Default route (http://127.0.0.1:8000/)
    path('api/data/', get_data, name='get_data'),  #  API endpoint (http://127.0.0.1:8000/api/data/)
]
