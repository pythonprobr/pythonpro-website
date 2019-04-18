from django.db import models
from django.urls import reverse


class Video(models.Model):
    title = models.CharField(max_length=100)
    vimeo_id = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def get_absolute_url(self):
        return reverse('promos:video', kwargs={'slug': self.slug})
