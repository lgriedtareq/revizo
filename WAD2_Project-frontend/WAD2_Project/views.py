from django.shortcuts import render

def home(request):
    return render(request, 'revizo/home.html')  # ✅ Ensure this template exists
