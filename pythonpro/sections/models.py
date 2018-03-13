from django.db import models


class Section(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    _module_slug = models.SlugField()
