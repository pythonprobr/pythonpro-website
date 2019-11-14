import uuid

from django.utils import timezone

from django.db import models


class UserSession(models.Model):
    class Meta:
        verbose_name = 'sessão'
        verbose_name_plural = 'sessões'

    created = models.DateTimeField('Criado em', default=timezone.now)
    updated = models.DateTimeField('Alterado em', auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.uuid)
