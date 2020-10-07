import uuid

from django.utils import timezone
from django.db import models
from django.db.models import JSONField

from pythonpro.core.models import User


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField('Criado em', default=timezone.now)
    updated = models.DateTimeField('Alterado em', auto_now=True)


class UserSession(BaseModel):
    class Meta:
        verbose_name = 'sessão'
        verbose_name_plural = 'sessões'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)

    def __str__(self):
        return str(self.uuid)


class PageView(BaseModel):
    class Meta:
        verbose_name = 'page view'
        verbose_name_plural = 'page views'

    session = models.ForeignKey(UserSession,
                                verbose_name='sessão',
                                on_delete=models.SET_NULL,
                                null=True)
    meta = JSONField()
