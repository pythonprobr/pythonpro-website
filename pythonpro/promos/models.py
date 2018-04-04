from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=100)
    vimeo_id = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
