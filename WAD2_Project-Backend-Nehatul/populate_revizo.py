import os
import random
import time
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WAD2_Project.settings')

import django

django.setup()
from revizo.models import UserProfile, Subject, Topic, Card, Explanation
from django.contrib.auth.models import User

def get_random_epoch_time(future=False):
    """Generate a random epoch time, either in the past or future."""
    now = datetime.now()
    if future:
        target_time = now + timedelta(days=random.randint(1, 14))
    else:
        target_time = now - timedelta(days=random.randint(1, 14))
    return int(target_time.timestamp())

def populate():
    users_data = [
        {"username": "user1", "email": "user1@example.com", "password": "pass123"},
        {"username": "user2", "email": "user2@example.com", "password": "pass456"},
        {"username": "user3", "email": "user3@example.com", "password": "pass789"}
    ]

    subjects_data = ["Math", "Science", "History", "English", "Computer Science"]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={"email": user_data["email"], "password": user_data["password"]}
        )
        
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        user_subjects = random.sample(subjects_data, 5)
        for subject_name in user_subjects:
            subject = Subject.objects.create(subject_name=subject_name, user=user_profile)


            
            num_topics = random.randint(2, 5)
            for i in range(num_topics):
                topic = Topic.objects.create(
                    topic_name=f"{subject_name} Topic {i+1}",
                    learning_score=random.randint(0, 100),
                    study_next=get_random_epoch_time(future=random.choice([True, False])),
                    subject=subject
                )
                
                num_cards = random.randint(1, 4)
                for j in range(num_cards):
                    card = Card.objects.create(
                        card_front=f"{topic.topic_name} Card {j+1} Front", 
                        card_back=f"{topic.topic_name} Card {j+1} Back", 
                        confidence_level=random.randint(0, 5), 
                        topic=topic
                    )
                    
                    if random.choice([True, False]):  # Add explanations to some cards
                        Explanation.objects.create(
                            ai_explanation=f"AI generated explanation for {card.card_front}",
                            ai_explanation_date=get_random_epoch_time(future=random.choice([True, False])),
                            card=card
                        )

if __name__ == "__main__":
    print("Starting population script...")
    populate()
    print("Database populated successfully!")
