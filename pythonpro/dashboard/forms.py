from django.forms import ModelForm

from pythonpro.dashboard.models import TopicInteraction


class TopicInteractionForm(ModelForm):
    class Meta:
        model = TopicInteraction
        fields = ('topic', 'user', 'topic_duration', 'total_watched_time', 'max_watched_time')
