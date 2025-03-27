from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Subject, Topic, Card, Explanation, UserProfile, AI
from django.urls import reverse
from datetime import timedelta
import json
from unittest.mock import patch


class SubjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.subject = Subject.objects.create(
            subject_name='Mathematics',
            user=self.user
        )

    def test_subject_creation(self):
        self.assertEqual(self.subject.subject_name, 'Mathematics')
        self.assertEqual(self.subject.user, self.user)
        self.assertEqual(str(self.subject), 'Mathematics')

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Subject.objects.create(
                subject_name='Mathematics',
                user=self.user
            )

class TopicModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.subject = Subject.objects.create(
            subject_name='Mathematics',
            user=self.user
        )
        self.topic = Topic.objects.create(
            topic_name='Calculus',
            subject=self.subject
        )

    def test_topic_creation(self):
        self.assertEqual(self.topic.topic_name, 'Calculus')
        self.assertEqual(self.topic.subject, self.subject)
        self.assertEqual(self.topic.learning_score, 0)
        self.assertTrue(isinstance(self.topic.study_next, timezone.datetime))
        self.assertEqual(str(self.topic), 'Calculus (Mathematics)')

    def test_unique_together_constraint(self):
        # Attempt to create a topic with the same name in the same subject
        with self.assertRaises(Exception):
            Topic.objects.create(
                topic_name='Calculus',
                subject=self.subject
            )

class CardModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.subject = Subject.objects.create(
            subject_name='Mathematics',
            user=self.user
        )
        self.topic = Topic.objects.create(
            topic_name='Calculus',
            subject=self.subject
        )
        self.card = Card.objects.create(
            card_front='What is a derivative?',
            card_back='Rate of change of a function',
            topic=self.topic
        )

    def test_card_creation(self):
        self.assertEqual(self.card.card_front, 'What is a derivative?')
        self.assertEqual(self.card.card_back, 'Rate of change of a function')
        self.assertEqual(self.card.topic, self.topic)
        self.assertEqual(self.card.confidence_level, 1)
        self.assertTrue(str(self.card).startswith('Card: What is a derivative?'))

class ExplanationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.subject = Subject.objects.create(
            subject_name='Mathematics',
            user=self.user
        )
        self.topic = Topic.objects.create(
            topic_name='Calculus',
            subject=self.subject
        )
        self.card = Card.objects.create(
            card_front='What is a derivative?',
            card_back='Rate of change of a function',
            topic=self.topic
        )
        self.explanation = Explanation.objects.create(
            ai_explanation='A derivative measures how a function changes as its input changes.',
            card=self.card
        )

    def test_explanation_creation(self):
        self.assertTrue(isinstance(self.explanation.created_at, timezone.datetime))
        self.assertEqual(str(self.explanation), f'Explanation for Card ID {self.card.id}')

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_profile_creation(self):
        self.assertEqual(str(self.profile), 'testuser')

class AITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.subject = Subject.objects.create(
            subject_name='Mathematics',
            user=self.user
        )
        self.topic = Topic.objects.create(
            topic_name='Calculus',
            subject=self.subject
        )
        self.card = Card.objects.create(
            card_front='What is a derivative?',
            card_back='Rate of change of a function',
            topic=self.topic
        )

    def test_get_AI_explanation_new(self):
        result = AI.get_AI_explanation(self.card.id)
        self.assertIsNotNone(result)
        self.assertIn('ai_explanation', result)
        self.assertIn(self.card.card_front, result['ai_explanation'])
        self.assertIn(self.card.card_back, result['ai_explanation'])

    def test_get_AI_explanation_existing(self):
        # Create an explanation
        explanation_text = 'Existing explanation'
        Explanation.objects.create(
            card=self.card,
            ai_explanation=explanation_text
        )
        
        # Get the explanation
        result = AI.get_AI_explanation(self.card.id)
        self.assertEqual(result['ai_explanation'], explanation_text)

    def test_get_AI_explanation_nonexistent_card(self):
        result = AI.get_AI_explanation(999)  # Non-existent card ID
        self.assertIsNone(result)

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='12345')
        
        # Create test data
        self.subject = Subject.objects.create(
            subject_name='Mathematics',
            user=self.user
        )
        self.topic = Topic.objects.create(
            topic_name='Calculus',
            subject=self.subject
        )
        self.card = Card.objects.create(
            card_front='What is a derivative?',
            card_back='Rate of change of a function',
            topic=self.topic
        )

    def test_home_view(self):
        response = self.client.get(reverse('revizo:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'revizo/home.html')

    def test_study_view_without_params(self):
        response = self.client.get(reverse('revizo:study'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('revizo:flashcards'))

    def test_study_view_with_params(self):
        response = self.client.get(
            reverse('revizo:study'),
            {'subject_id': self.subject.id, 'topic_id': self.topic.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'revizo/study.html')

    @patch('revizo.utils.claude_helper.ClaudeHelper.generate_flashcard_explanation')
    def test_get_card_explanation(self, mock_generate):
        mock_generate.return_value = "Test explanation"
        
        data = {'card_id': self.card.id}
        response = self.client.post(
            reverse('revizo:get_card_explanation'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data.get('success'))
        self.assertEqual(response_data.get('explanation'), "Test explanation")
        
        mock_generate.assert_called_once_with(self.card.card_front, self.card.card_back)

    def test_get_card_explanation_invalid_method(self):
        response = self.client.get(
            reverse('revizo:get_card_explanation'),
            {'card_id': self.card.id}
        )
        self.assertEqual(response.status_code, 405)

    def test_flashcards_view(self):
        response = self.client.get(reverse('revizo:flashcards'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'revizo/flashcards.html')

    def test_about_view(self):
        response = self.client.get(reverse('revizo:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'revizo/about.html')

    def test_add_flashcard(self):
        data = {
            'topic': self.topic.id,
            'card_front': 'Test front',
            'card_back': 'Test back'
        }
        response = self.client.post(reverse('revizo:add_flashcard'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_filter_flashcards(self):
        response = self.client.get(
            reverse('revizo:filter_flashcards'),
            {'subject_id': self.subject.id, 'topic_id': self.topic.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('flashcards', response.json())

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse('revizo:flashcards'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertRedirects(response, '/accounts/login/?next=/revizo/flashcards/')
