from django.shortcuts import render
from django.http import JsonResponse
from revizo.models import Subject, Topic, Card
from django.shortcuts import render
from revizo.forms import UserForm, UserProfileForm, FlashCardForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def home(request):
    context_dict = {}
    response = render(request, 'revizo/home.html', context=context_dict)
    
    return response

def about(request):
    context_dict = {}

    return render(request, 'revizo/about.html', context=context_dict)

def register(request):
    
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'revizo/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('revizo:index'))
            else:
                return HttpResponse("Your Revizo account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'revizo/login.html')
    
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('revizo/home.html'))

def flashcards(request):
    subjects = Subject.objects.all()
    topics = Topic.objects.none()
    flashcards = Card.objects.none()

    subject_id = request.GET.get("subject")
    topic_id = request.GET.get("topic")

    if subject_id:
        topics = Topic.objects.filter(subject_id=subject_id)
    
    if topic_id:
        flashcards = Card.objects.filter(topic_id=topic_id)

    return render(request, 'revizo/flashcards.html', {'subjects': subjects, "topics": topics, "flashcards": flashcards})
    
def add_flashcard(request):
    if request.method == 'POST':
        form = FlashCardForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Invalid request method"})

def filter_flashcards(request):
    topic_id = request.GET.get("topic_id")
    flashcards = Card.objects.filter(topic_id=topic_id).select_related("topic__subject")

    flashcard_list = [
        {
            "id": card.id,
            "subject_name": card.topic.subject.subject_name,
            "topic_name": card.topic.topic_name,
            "card_front": card.card_front,
            "card_back": card.card_back
        }
        for card in flashcards
    ]

    return JsonResponse({"flashcards": flashcard_list})


def delete_flashcard(request, pk):
    if request.method == "POST":
        try:
            card = Card.objects.get(pk=pk)
            card.delete()
            return JsonResponse({"success": True})
        except Card.DoesNotExist:
            return JsonResponse({"success": False, "error": "Flashcard not found."})
    
    return JsonResponse({"success": False, "error": "Invalid request."})

def get_topics(request):
    subject_id = request.GET.get("subject_id")
    if subject_id:
        topics = Topic.objects.filter(subject_id=subject_id).values("id", "topic_name")
        return JsonResponse(list(topics), safe=False)
    return JsonResponse({"error": "Missing subject_id"}, status=400)

def filter_flashcards(request):
    topic_id = request.GET.get("topic_id")
    flashcards = Card.objects.filter(topic_id=topic_id).select_related("topic__subject")
    flashcard_list = [{
        "id": card.id,
        "subject_name": card.topic.subject.subject_name,
        "topic_name": card.topic.topic_name,
        "card_front": card.card_front,
        "card_back": card.card_back
    } for card in flashcards]
    return JsonResponse({"flashcards": flashcard_list})

def edit_flashcard(request, pk):
    if request.method == 'POST':
        try:
            card = Card.objects.get(pk=pk)
            card.card_front = request.POST.get("card_front")
            card.card_back = request.POST.get("card_back")
            card.save()
            return JsonResponse({"success": True})
        except Card.DoesNotExist:
            return JsonResponse({"success": False, "error": "Flashcard not found."})
    
    return JsonResponse({"success": False, "error": "Invalid request."})

def study(request):
    return render(request, 'revizo/study.html')

def contact_us(request):
    return render(request, 'revizo/contact.html')
