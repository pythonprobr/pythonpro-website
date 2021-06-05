from django.contrib.auth import get_user_model
from django.db import models


class SubscriptionType(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'Assinatura: {self.name}'

    class Meta:
        verbose_name = 'Tipo de Assinatura'
        verbose_name_plural = 'Tipos de Assinaturas'


class PaymentItemConfigToSubscriptionType(models.Model):
    payment_item = models.OneToOneField('django_pagarme.PagarmeItemConfig', null=False, on_delete=models.CASCADE,
                                        related_name='subscription_type_relation')
    subscription_type = models.ForeignKey(SubscriptionType, null=False, on_delete=models.CASCADE,
                                          related_name='payment_items_relation')

    def __str__(self):
        return f'{self.payment_item} -> {self.subscription_type}'


class Subscription(models.Model):
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'

    class Status(models.TextChoices):
        ACTIVE = 'A', 'Ativo'
        INACTIVE = 'I', 'Inativo'

    status = models.CharField(max_length=1, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment = models.OneToOneField('django_pagarme.PagarmePayment', on_delete=models.DO_NOTHING, null=True)
    subscription_types = models.ManyToManyField(SubscriptionType, related_name='subscriptions')
    subscriber = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True,
                                   related_name='subscriptions')
    responsible = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True,
                                    related_name='created_subscriptions')
    observation = models.TextField(verbose_name='Observação', blank=True, default='')
