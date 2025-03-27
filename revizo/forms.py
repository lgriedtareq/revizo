from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Card, Subject, Topic

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(error_messages={
        'unique': 'A user with that username already exists.'
    })

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ()

class SubjectForm (forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["subject_name"]

class TopicForm (forms.ModelForm):
     class Meta:
        model = Topic
        fields = ["topic_name", "subject"]

class FlashCardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["card_front", "card_back", "topic"]
        widgets = {
            "card_front": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "card_back": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "topic": forms.Select(attrs={"class": "form-control"})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['topic'].queryset = Topic.objects.filter(subject__user=user)

class FlashCardFilterForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True, empty_label="Select Subject")
    topic = forms.ModelChoiceField(queryset=Topic.objects.none(), required=True, empty_label="Select Topic")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "subject" in self.data:
            try:
                subject_id = int(self.data.get("subject"))
                self.fields["topic"].queryset = Topic.objects.filter(subject_id=subject_id).order_by("topic_name")
            except (ValueError, TypeError):
                pass
        else:
            self.fields["topic"].queryset = Topic.objects.none()
