from django.db import models


class SubscriptionType(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'Assinatura: {self.name}'

    class Meta:
        verbose_name = 'Tipo de Assinatura'
        verbose_name_plural = 'Tipos de Assinaturas'
