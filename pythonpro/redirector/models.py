from django.utils import timezone

from django.db import models


class Redirect(models.Model):
    created = models.DateTimeField("Criado em", default=timezone.now)
    updated = models.DateTimeField("Alterado em", auto_now=True)
    slug = models.SlugField(primary_key=True)
    url = models.URLField(null=True, blank=True)
    use_javascript = models.BooleanField(default=False)

    def __str__(self):
        return self.slug


class RedirectLink(models.Model):
    created = models.DateTimeField("Criado em", default=timezone.now)
    updated = models.DateTimeField("Alterado em", auto_now=True)
    redirect = models.ForeignKey(Redirect, on_delete=models.PROTECT, related_name='links')
    url = models.URLField()
    total_access = models.BigIntegerField(default=0)
