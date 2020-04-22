from django.utils import timezone

from django.db import models


class Redirect(models.Model):
    created = models.DateTimeField("Criado em", default=timezone.now)
    updated = models.DateTimeField("Alterado em", auto_now=True)
    slug = models.SlugField(primary_key=True)
    url = models.URLField(null=True, blank=True)


class RedirectLink(models.Model):
    created = models.DateTimeField("Criado em", default=timezone.now)
    updated = models.DateTimeField("Alterado em", auto_now=True)
    redirect = models.ForeignKey(Redirect, on_delete=models.PROTECT, related_name='links')
    url = models.URLField()
