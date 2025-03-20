from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    subject_name = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_subjects")

    def __str__(self):
        return self.subject_name

class Topic(models.Model):
    topic_name = models.CharField(max_length=128)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="subject_topics")

    class Meta:
        unique_together = ('topic_name', 'subject')  

    def __str__(self):
        return f"{self.topic_name} ({self.subject.subject_name})"

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_front = models.TextField()
    card_back = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topic_cards")

    def __str__(self):
        return f"Card: {self.card_front[:30]}... ({self.topic.topic_name})"

class Explanation(models.Model):
    ai_explanation = models.TextField()
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="card_explanations")

    def __str__(self):
        return f"Explanation for Card ID {self.card.id}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username

""" building basis,  rememeber to add other fields such as scores and dates once the basic functionality is working """