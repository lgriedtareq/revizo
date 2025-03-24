from django.db import models,transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import os,json
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

ONE_DAY = 86400
THREE_DAYS = 259200
ONE_WEEK = 604800
TWO_WEEKS = 1209600
FOUR_WEEKS = 2419200
CONFIDENCE_LEVELS = [1, 2, 3]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True, unique=True)
    subject_name = models.CharField(max_length=128)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="subjects")
    
    def __str__(self):
        return self.subject_name


class Topic(models.Model):
    topic_id = models.AutoField(primary_key=True, unique=True)
    topic_name = models.CharField(max_length=128)
    learning_score = models.IntegerField(default=0)
    study_next = models.IntegerField(default=0)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    
    def __str__(self):
        return self.topic_name


class Card(models.Model):
    card_id = models.AutoField(primary_key=True, unique=True)
    card_front = models.TextField()
    card_back = models.TextField()
    confidence_level = models.IntegerField(default=0)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="cards")
    
    def __str__(self):
        return f"Front: {self.card_front}\nBack: {self.card_back}"
    
class Explanation(models.Model):
    explain_id = models.AutoField(primary_key=True, unique=True)
    ai_explanation = models.TextField()
    ai_explanation_date = models.IntegerField(default=0)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="explanations")
    
    def __str__(self):
        return self.ai_explanation


class Data:
    """Handles interaction with the database using Django ORM."""

    @staticmethod
    def create_subject(subject_name: str, user_profile: UserProfile):
        """Creates a new subject in the database for a specific user."""
        Subject.objects.create(subject_name=subject_name, user=user_profile)

    @staticmethod
    def create_topic(topic_name: str, subject_name: str, user_profile: UserProfile):
        """Creates a new topic associated with a specific subject in the database for a specific user."""
        subject = Subject.objects.get(subject_name=subject_name, user=user_profile)
        Topic.objects.create(topic_name=topic_name, subject=subject)

    @staticmethod
    def create_flash_card(card_front: str, card_back: str, topic_name: str, user_profile: UserProfile):
        """Creates a new flash card associated with a specific topic in the database for a specific user."""
        topic = Topic.objects.get(topic_name=topic_name, subject__user=user_profile)
        Card.objects.create(card_front=card_front, card_back=card_back, topic=topic, confidence_level=1)

    @staticmethod
    def get_subjects(user_profile: UserProfile):
        """Retrieves all subjects for a specific user."""
        return Subject.objects.filter(user=user_profile).values('subject_name')

    @staticmethod
    def get_topics_by_subject(user_profile: UserProfile, picked_subject: str):
        """Retrieves topics related to a specific subject for a specific user."""
        return Topic.objects.filter(subject__user=user_profile, subject__subject_name=picked_subject).values('topic_name')

    @staticmethod
    def get_flash_cards_by_topic(user_profile: UserProfile, topic_name: str):
        """Retrieves flash cards associated with a specific topic for the current user."""
        return Card.objects.filter(topic__subject__user=user_profile, topic__topic_name=topic_name).values('card_id', 'card_front', 'card_back', 'confidence_level')

    @staticmethod
    def get_suggested_topics(user_profile: UserProfile):
        """Retrieves topics with an overdue 'Study_Next' timestamp for the current user."""
        current_time = int(timezone.now().timestamp())
        return Topic.objects.filter(subject__user=user_profile, study_next__lte=current_time).values('subject__subject_name', 'topic_name', 'learning_score')

    @staticmethod
    def get_AI_explanation(user_profile: UserProfile, card_id: int):
        """Retrieves AI explanation for a specific flash card belonging to the current user."""
        return Explanation.objects.filter(card__topic__subject__user=user_profile, card_id=card_id).values('ai_explanation', 'ai_explanation_date').first()

    @staticmethod
    def get_flash_card_front(user_profile: UserProfile, card_id: int):
        """Retrieves the front side of a flash card belonging to the current user."""
        return Card.objects.filter(topic__subject__user=user_profile, card_id=card_id).values('card_front').first()

    @staticmethod
    def get_percent_of_secured_flash_cards(user_profile: UserProfile, topic_name: str):
        """Calculates the percentage of flash cards with confidence level 3 for a specific topic for the current user."""
        total_flash_cards = Card.objects.filter(topic__subject__user=user_profile, topic__topic_name=topic_name).count()
        secured_flash_cards = Card.objects.filter(topic__subject__user=user_profile, topic__topic_name=topic_name, confidence_level=3).count()
        if total_flash_cards > 0:
            return (secured_flash_cards * 100.0) / total_flash_cards
        return 0

    @staticmethod
    def get_learning_score(user_profile: UserProfile, topic_name: str):
        """Retrieves the learning score for a specific topic for the current user."""
        try:
            topic = Topic.objects.get(topic_name=topic_name, subject__user=user_profile)
            return topic.learning_score
        except Topic.DoesNotExist:
            return 0  # Return 0 if the topic is not found

    @staticmethod
    def update_flash_card(user_profile: UserProfile, card_id: int, card_front: str, card_back: str):
        """Updates the front and back sides of a flash card for the current user."""
        Card.objects.filter(card_id=card_id, topic__subject__user=user_profile).update(card_front=card_front, card_back=card_back)

    @staticmethod
    def update_confidence_level(user_profile: UserProfile, card_id: int, new_confidence_level: int):
        """Updates the confidence level of a flash card for the current user."""
        Card.objects.filter(card_id=card_id, topic__subject__user=user_profile).update(confidence_level=new_confidence_level)

    @staticmethod
    def update_AI_explanation(user_profile: UserProfile, card_id: int, explanation: str, time: int):
        """Updates or inserts an AI explanation for a specific flash card for the current user."""
        Explanation.objects.update_or_create(
            card_id=card_id,
            card__topic__subject__user=user_profile,
            defaults={'ai_explanation': explanation, 'ai_explanation_date': time}
        )

    @staticmethod
    def update_Study_Next_and_Learning_Score(user_profile: UserProfile, score: int, time: int, topic_name: str):
        """Updates the learning score and 'Study_Next' timestamp for a specific topic for the current user."""
        current_time = timezone.now().timestamp()
        
        if score <= 30:
            time = ONE_DAY + current_time
        elif score <= 50:
            time = THREE_DAYS + current_time
        elif score <= 70:
            time = ONE_WEEK + current_time
        else:
            time = TWO_WEEKS + current_time
                
        Topic.objects.filter(topic_name=topic_name, subject__user=user_profile).update(learning_score=score, study_next=time)

    @staticmethod
    @transaction.atomic
    def remove_flash_cards(user_profile: UserProfile, card_id: int):
        """Removes a flash card and its associated AI explanation from the database for the current user."""
        try:
            # Ensure the card exists for the current user
            card = Card.objects.get(topic__subject__user=user_profile, card_id=card_id)
            
            # Delete related AI explanations
            Explanation.objects.filter(card=card).delete()
            
            # Delete the flash card
            card.delete()
        except ObjectDoesNotExist:
            raise ValueError("Flash card not found or not associated with the current user.")
        
    @staticmethod
    @transaction.atomic
    def remove_topic(user_profile: UserProfile, topic_name: str):
        """Removes a topic and its associated flash cards and AI explanation from the database for the current user."""
        try:
            # Ensure the topic exists for the current user
            topic = Topic.objects.get(subject__user=user_profile, topic_name=topic_name)
            
            # Delete related flash cards and explanations
            Explanation.objects.filter(card__topic=topic).delete()
            Card.objects.filter(topic=topic).delete()
            
            # Delete the topic
            topic.delete()
        except ObjectDoesNotExist:
            raise ValueError("Topic not found or not associated with the current user.")
        
    @staticmethod
    @transaction.atomic
    def remove_subject(user_profile: UserProfile, subject_name: str):
        """Removes a subject and all associated topics, flash cards, and AI explanation from the database for the current user."""
        try:
            # Ensure the subject exists for the current user
            subject = Subject.objects.get(subject_name=subject_name, user=user_profile)
            
            # Delete all related topics, flash cards, and explanations
            Explanation.objects.filter(card__topic__subject=subject).delete()
            Card.objects.filter(topic__subject=subject).delete()
            Topic.objects.filter(subject=subject).delete()
            
            # Delete the subject
            subject.delete()
        except ObjectDoesNotExist:
            raise ValueError("Subject not found or not associated with the current user.")



class AI:
    __CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_AI_explanation(self, card_id: int):
        """Retrieve AI explanation of current flashcard."""
        explanation = self.__get_AI_explanation_from_db(card_id)
        current_time = timezone.now().timestamp()
        if explanation is None or (explanation['ai_explanation_date'] + FOUR_WEEKS) < current_time:
            self.__get_AI_explanation_from_gpt(card_id)
            sleep(0.1)  # prevent sync issues
            explanation = self.__get_AI_explanation_from_db(card_id)
        return explanation

    def __get_AI_explanation_from_db(self, card_id: int):
        """Retrieves AI explanation from the database using Data class."""
        return Data.get_AI_explanation(card_id)

    def __get_AI_explanation_from_gpt(self, card_id: int):
        """Fetches AI explanation from GPT and updates the database using Data class."""
        try:
            # Get card front from the database using Data class
            card_front = Data.get_flash_card_front(card_id)
            
            # Create a prompt for GPT
            completion = self.__CLIENT.chat.completions.create(
                model="gpt-3.5-turbo-1106", 
                response_format="json",
                messages=[
                    {"role": "system", "content": """You are an A level Teacher, 
                        at the best Sixth Form in the United Kingdom, 
                        you are able to explain any concept in a few sentences.
                        return it in JSON and in the following manner 'Explanation': 
                        and make your sentences short and each should be on their own line 
                        and GIVE only 1 explanation."""},
                    {"role": "user", "content": f"Explain the flash card: {card_front}"}
                ]
            )
            
            # Retrieve explanation from GPT
            explanation = json.loads(completion.choices[0].message.content).get("Explanation", "")
            
            # Get the time of explanation creation
            time_created = completion.created

            # Update or insert the explanation in the database using Data class
            Data.update_AI_explanation(card_id, explanation, time_created)
        except Exception as e:
            # Handle errors related to GPT
            print(f"Error retrieving AI explanation: {e}")