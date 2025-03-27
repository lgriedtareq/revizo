import json
from django.shortcuts import render
from django.http import JsonResponse
from revizo.models import Subject, Topic, Card, UserProfile, AI
from django.shortcuts import render
from revizo.forms import UserForm, UserProfileForm, FlashCardForm, SubjectForm, TopicForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .utils.claude_helper import ClaudeHelper
from django.contrib import messages


def home(request):
    context_dict = {}
    
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        context_dict['subjects'] = Subject.objects.filter(user=request.user)
        
        # Get bottom 5 topics by learning score
        suggested_topics = Topic.objects.filter(
            subject__user=request.user,
            study_next__lte=timezone.now()
        ).select_related('subject').order_by('learning_score')[:5]
        
        context_dict['suggested_topics'] = [
            {
                'subject_name': topic.subject.subject_name,
                'topic_name': topic.topic_name,
                'learning_score': topic.learning_score,
                'subject_id': topic.subject.id,
                'topic_id': topic.id
            }
            for topic in suggested_topics
        ]
    else:
        context_dict['subjects'] = []
        context_dict['suggested_topics'] = []
    
    return render(request, 'revizo/home.html', context=context_dict)
    
def about(request):
    return render(request, 'revizo/about.html')

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
            profile.save()
            
            # Automatically log in the user after registration
            login(request, user)
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'revizo/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    error = None;
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('revizo:home'))
            else:
                return HttpResponse("Your Revizo account is disabled.")
        else:
            error = "Invalid login details supplied."
    return render(request, 'revizo/login.html')
    
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('revizo:home'))

@login_required
def flashcards(request):
    user_profile = UserProfile.objects.get(user=request.user)
    subjects = Subject.objects.filter(user=request.user).distinct()
    
    subject_id = request.GET.get("subject")
    topic_id = request.GET.get("topic")
    
    if subject_id:
        topics = Topic.objects.filter(
            subject_id=subject_id,
            subject__user=request.user
        ).select_related('subject').distinct()
        flashcards = Card.objects.filter(
            topic__subject_id=subject_id,
            topic__subject__user=request.user
        ).select_related('topic', 'topic__subject')
    else:
        topics = Topic.objects.filter(
            subject__user=request.user
        ).select_related('subject').distinct()
        flashcards = Card.objects.filter(
            topic__subject__user=request.user
        ).select_related('topic', 'topic__subject')

    if topic_id:
        flashcards = flashcards.filter(topic__id=topic_id)

    flashcards_json = serialize("json", flashcards)
    
    return render(request, 'revizo/flashcards.html', {
        'subjects': subjects,
        'topics': topics,
        'flashcards': flashcards,
        'flashcards_json': flashcards_json,
    })

@login_required
def add_flashcard(request):
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            topic_id = request.POST.get('topic')
            card_front = request.POST.get('card_front')
            card_back = request.POST.get('card_back')
            
            topic = Topic.objects.get(id=topic_id, subject__user=request.user)
            
            Card.objects.create(
                card_front=card_front,
                card_back=card_back,
                topic=topic,
                confidence_level=1
            )
            return JsonResponse({"success": True})
        except Topic.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid topic."})
        except UserProfile.DoesNotExist:
            return JsonResponse({"success": False, "error": "User profile not found."})
    
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def filter_flashcards(request):
    user_profile = UserProfile.objects.get(user=request.user)
    topic_id = request.GET.get("topic_id")
    subject_id = request.GET.get("subject_id")
    
    flashcards = Card.objects.filter(topic__subject__user=request.user)
    
    if subject_id:
        flashcards = flashcards.filter(topic__subject_id=subject_id)
    if topic_id:
        flashcards = flashcards.filter(topic__id=topic_id)

    flashcard_list = [
        {
            "id": card.id,
            "subject_name": card.topic.subject.subject_name,
            "topic_name": card.topic.topic_name,
            "card_front": card.card_front,
            "card_back": card.card_back,
            "confidence_level": card.confidence_level
        }
        for card in flashcards
    ]

    return JsonResponse({"flashcards": flashcard_list})

@login_required
def delete_flashcard(request, pk):
    if request.method == "POST":
        try:
            card = Card.objects.get(id=pk, topic__subject__user=request.user)
            card.delete()
            return JsonResponse({"success": True})
        except Card.DoesNotExist:
            return JsonResponse({"success": False, "error": "Card not found"})
    
    return JsonResponse({"success": False, "error": "Invalid request."})

@login_required
def get_topics(request):
    try:
        subject_id = request.GET.get("subject_id")
        print(f"Received request for topics with subject_id: {subject_id}")
        print(f"User: {request.user}")
        
        if not subject_id:
            print("No subject_id provided")
            return JsonResponse({"error": "Missing subject_id"}, status=400)
        
        # Ensure the subject belongs to the current user
        subject = Subject.objects.get(id=subject_id, user=request.user)
        print(f"Found subject: {subject.subject_name}")
        
        topics = Topic.objects.filter(
            subject=subject
        ).values("id", "topic_name").distinct()
        
        topics_list = list(topics)
        print(f"Found topics: {topics_list}")
        
        return JsonResponse(topics_list, safe=False)
    except Subject.DoesNotExist:
        print(f"Subject not found or access denied for subject_id: {subject_id}")
        return JsonResponse({"error": "Subject not found or access denied"}, status=404)
    except Exception as e:
        print(f"Error in get_topics: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def edit_flashcard(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            card = Card.objects.get(id=pk, topic__subject__user=request.user)
            card.card_front = data.get("front")
            card.card_back = data.get("back")
            card.save()
            return JsonResponse({"success": True})
        except Card.DoesNotExist:
            return JsonResponse({"success": False, "error": "Card not found"})

@login_required
def study(request):
    subject_id = request.GET.get('subject_id')
    topic_id = request.GET.get('topic_id')
    
    if not subject_id or not topic_id:
        return redirect('revizo:flashcards')
    
    # Get cards for the selected topic
    cards = Card.objects.filter(
        topic_id=topic_id,
        topic__subject_id=subject_id,
        topic__subject__user=request.user
    ).select_related('topic', 'topic__subject')
    
    # Convert cards to JSON format
    cards_data = [
        {
            'id': card.id,
            'card_front': card.card_front,
            'card_back': card.card_back,
            'confidence_level': card.confidence_level,
            'subject_name': card.topic.subject.subject_name,
            'topic_name': card.topic.topic_name
        }
        for card in cards
    ]
    
    # Serialize the cards data to JSON
    cards_json = json.dumps(cards_data)
    
    return render(request, 'revizo/study.html', {
        'cards': cards_json,
        'subject_id': subject_id,
        'topic_id': topic_id
    })

@login_required
def contact(request):
    return render(request, 'revizo/contact.html')

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': request.session.session_key
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return JsonResponse({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': request.session.session_key
            })
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def api_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out successfully'})

@login_required
def update_confidence(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            confidence_level = data.get('confidence_level')
            
            if confidence_level not in [1, 2, 3]:
                return JsonResponse({"success": False, "error": "Invalid confidence level"})
                
            card = Card.objects.get(id=pk, topic__subject__user=request.user)
            card.confidence_level = confidence_level
            card.save()
            
            # Calculate the topic's learning score based on all cards' confidence levels
            topic = card.topic
            cards = Card.objects.filter(topic=topic)
            
            # Convert confidence levels to percentages and calculate average
            confidence_percentages = {
                1: 33.3,  # "Still Learning"
                2: 66.7,  # "Getting There"
                3: 100.0  # "Know It!"
            }
            
            total_percentage = sum(confidence_percentages[card.confidence_level] for card in cards)
            avg_percentage = total_percentage / cards.count()
            
            # Update the topic's learning score
            topic.learning_score = round(avg_percentage)
            topic.save()
            
            return JsonResponse({
                "success": True,
                "learning_score": topic.learning_score
            })
        except Card.DoesNotExist:
            return JsonResponse({"success": False, "error": "Card not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

@login_required
def get_ai_explanation(request, card_id):
    try:
        # Get the card and ensure it belongs to the current user
        card = Card.objects.get(id=card_id, topic__subject__user=request.user)
        
        # Create an instance of ClaudeHelper
        claude = ClaudeHelper()
        
        # Get AI explanation
        explanation = claude.generate_flashcard_explanation(card.card_front, card.card_back)
        
        return JsonResponse({
            "success": True,
            "explanation": explanation
        })
    except Card.DoesNotExist:
        return JsonResponse({"success": False, "error": "Card not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def get_card_explanation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            card_id = data.get('card_id')
            
            if not card_id:
                return JsonResponse({"error": "Missing card_id"}, status=400)
            
            # Get the card and ensure it belongs to the current user
            card = Card.objects.get(id=card_id, topic__subject__user=request.user)
            
            # Create an instance of ClaudeHelper and get explanation
            claude = ClaudeHelper()
            explanation = claude.generate_flashcard_explanation(card.card_front, card.card_back)
            
            return JsonResponse({
                "success": True,
                "explanation": explanation
            })
        except Card.DoesNotExist:
            return JsonResponse({"error": "Card not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def get_related_cards(request):
    """View to get AI-generated suggestions for related flashcards"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            card_content = data.get('content')
            
            if not card_content:
                return JsonResponse({'error': 'Missing card content'}, status=400)
            
            claude = ClaudeHelper()
            suggestions = claude.suggest_related_cards(card_content)
            
            return JsonResponse({'suggestions': suggestions})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def create_flashcard(request):
    if request.method == 'POST':
        form = FlashCardForm(request.POST, user=request.user)
        if form.is_valid():
            flashcard = form.save(commit=False)
            flashcard.user = request.user
            flashcard.save()
            messages.success(request, 'Flashcard created successfully!')
            return redirect('revizo:flashcards')
    else:
        form = FlashCardForm(user=request.user)
    
    # Get user's subjects
    user_subjects = Subject.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'user_subjects': user_subjects,
    }
    return render(request, 'revizo/create_flashcard.html', context)

@login_required
def create_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.user = request.user
            subject.save()
            messages.success(request, 'Subject created successfully! You can now create a topic for it.')
            return redirect('revizo:create_organization')
    else:
        form = SubjectForm()
    
    return render(request, 'revizo/create_subject.html', {'form': form})

@login_required
def create_topic(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            if topic.subject.user == request.user:
                # Check if topic already exists for this subject
                existing_topic = Topic.objects.filter(
                    subject=topic.subject,
                    topic_name=topic.topic_name
                ).exists()
                
                if existing_topic:
                    messages.error(request, 'A topic with this name already exists in this subject.')
                else:
                    topic.save()
                    messages.success(request, 'Topic created successfully!')
                return redirect('revizo:create_organization')
            else:
                messages.error(request, 'You do not have permission to add topics to this subject.')
    else:
        form = TopicForm()
    
    # Filter subjects to only show user's subjects
    form.fields['subject'].queryset = Subject.objects.filter(user=request.user)
    
    return render(request, 'revizo/create_topic.html', {'form': form})

@login_required
def create_organization(request):
    subjects = Subject.objects.filter(user=request.user)
    return render(request, 'revizo/create_organization.html', {
        'subjects': subjects,
        'messages': messages.get_messages(request)
    })
