from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models


class SubscriptionType(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=128)
    email_marketing_tags = ArrayField(models.CharField(max_length=64), default=list)
    discourse_groups = ArrayField(models.CharField(max_length=64), default=list)
    include_on_cohort = models.BooleanField(default=False, verbose_name='Incluir na última turma')

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
    payment = models.OneToOneField('django_pagarme.PagarmePayment', on_delete=models.DO_NOTHING, null=True, blank=True)
    subscription_types = models.ManyToManyField(SubscriptionType, related_name='subscriptions')
    subscriber = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True,
                                   related_name='subscriptions')
    responsible = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True,
                                    related_name='created_subscriptions')
    observation = models.TextField(verbose_name='Observação', blank=True, default='')
    activated_at = models.DateTimeField(null=True, default=None)
    memberkit_user_id = models.IntegerField(null=True)

    @property
    def include_on_cohort(self):
        return self.subscription_types.filter(include_on_cohort=True).exists()

    @property
    def email_marketing_tags(self):
        tags = []
        for s in self.subscription_types.all():
            tags.extend(s.email_marketing_tags)
        return [s.email_marketing_tags for s in self.subscription_types.all()]

    @property
    def discourse_groups(self):
        groups = []
        for s in self.subscription_types.all():
            groups.extend(s.email_marketing_tags)
        return [s.discourse_groups for s in self.subscription_types.all()]

    def __str__(self):
        return f'Assinatura: {self.id} de {self.subscriber}'
