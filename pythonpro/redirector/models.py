from django.db import models


# Create your models here.
class Redirect(models.Model):
    url = models.URLField()
    slug = models.SlugField(primary_key=True)
