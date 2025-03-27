from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subject(models.Model):
    subject_name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_subjects")

    class Meta:
        unique_together = ('subject_name', 'user')

    def __str__(self):
        return self.subject_name

class Topic(models.Model):
    topic_name = models.CharField(max_length=128)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="subject_topics")
    learning_score = models.IntegerField(default=0)
    study_next = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.topic_name} ({self.subject.subject_name})"

    class Meta:
        unique_together = ('topic_name', 'subject')

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_front = models.TextField()
    card_back = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topic_cards")
    confidence_level = models.IntegerField(default=1)

    def __str__(self):
        return f"Card: {self.card_front[:30]}... ({self.topic.topic_name})"

class Explanation(models.Model):
    ai_explanation = models.TextField()
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="card_explanations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Explanation for Card ID {self.card.id}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class AI:
    @staticmethod
    def get_AI_explanation(card_id):
        try:
            card = Card.objects.get(id=card_id)
            
            # Check for existing explanation less than 4 weeks old
            recent_explanation = Explanation.objects.filter(
                card=card,
                created_at__gte=timezone.now() - timezone.timedelta(weeks=4)
            ).first()
            
            if recent_explanation:
                return {'ai_explanation': recent_explanation.ai_explanation}
            
            # If no recent explanation exists, create a new one
            # For now, we'll return a simple concatenation of front and back
            # This should be replaced with actual AI integration
            explanation = f"Front: {card.card_front}\nBack: {card.card_back}"
            
            # Save the new explanation
            new_explanation = Explanation.objects.create(
                card=card,
                ai_explanation=explanation
            )
            
            return {'ai_explanation': explanation}
            
        except Card.DoesNotExist:
            return None
