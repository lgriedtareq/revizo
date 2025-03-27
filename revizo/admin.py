from django.contrib import admin
from revizo.models import Subject, Topic, Card, UserProfile, Explanation

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'user')
    list_filter = ('user',)
    search_fields = ('subject_name',)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_name', 'subject')
    list_filter = ('subject',)
    search_fields = ('topic_name',)

class CardAdmin(admin.ModelAdmin):
    list_display = ('card_front', 'card_back', 'topic')
    list_filter = ('topic', 'topic__subject')
    search_fields = ('card_front', 'card_back')

# Register your models here.
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(UserProfile)
admin.site.register(Explanation)
