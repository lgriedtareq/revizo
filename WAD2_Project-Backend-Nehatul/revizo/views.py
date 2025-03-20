from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import MyModel  # Ensure MyModel exists in models.py

# Create your views here.
def some_view(request):
    return HttpResponse("Hello, this is the Revizo app!")

def get_data(request): 
    data = list(MyModel.objects.values())  # Convert QuerySet to list
    return JsonResponse(data, safe=False)

