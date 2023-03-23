from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

YEAR_IN_DAYS = 365
_ETERNAL_IN_HUMAN_LIFE_DAYS = YEAR_IN_DAYS * 200


class SubscriptionType(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=128)
    email_marketing_tags = ArrayField(models.CharField(max_length=64), default=list)
    discourse_groups = ArrayField(models.CharField(max_length=64), default=list)
    include_on_cohort = models.BooleanField(default=False, verbose_name='Incluir na última turma')
    days_of_access = models.IntegerField(default=YEAR_IN_DAYS)
    has_discord_access = models.BooleanField(default=False)

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
        ACTIVE = 'A', 'Ativa'
        INACTIVE = 'I', 'Inativa'

    status = models.CharField(max_length=1, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    days_of_access = models.IntegerField(default=YEAR_IN_DAYS)
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
    def name(self):
        return ' - '.join(s.name for s in self.subscription_types.all())

    @property
    def expires_at(self):
        if self.activated_at:
            return self.activated_at + timedelta(days=self.days_of_access)
        return '--'

    @property
    def remaining_days(self):
        if self.activated_at:
            consumed_timedelta = timezone.now() - self.activated_at
            return max(0, self.days_of_access - consumed_timedelta.days)
        return 0

    @property
    def email_marketing_tags(self):
        tags = []
        for s in self.subscription_types.all():
            tags.extend(s.email_marketing_tags)
        return tags

    @property
    def discourse_groups(self):
        groups = []
        for s in self.subscription_types.all():
            groups.extend(s.discourse_groups)
        return groups

    def __str__(self):
        return f'Assinatura: {self.id} de {self.subscriber}'
