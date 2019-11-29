from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from pythonpro.modules.facade import get_topic_model


class TopicInteraction(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', 'topic', '-creation']),
            models.Index(fields=['-creation', ]),
        ]
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'

    creation = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(get_topic_model(), on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    topic_duration = models.IntegerField('Duração do Tópico')  # seconds
    total_watched_time = models.IntegerField('Tempo assistindo o Tópico')  # seconds
    max_watched_time = models.IntegerField('Tempo até onde assistiu')  # seconds

    def get_topic_url(self):
        return reverse('topics:detail', kwargs={'slug': self.topic.slug})

    def get_topic_title(self):
        return self.topic.title
