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
    old_days_of_access = models.IntegerField(default=YEAR_IN_DAYS, db_column='days_of_access')
    payment = models.OneToOneField('django_pagarme.PagarmePayment', on_delete=models.DO_NOTHING, null=True, blank=True)
    subscription_types = models.ManyToManyField(SubscriptionType, related_name='subscriptions')
    subscriber = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='subscriptions')
    responsible = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True,
                                    related_name='created_subscriptions')
    observation = models.TextField(verbose_name='Observação', blank=True, default='')
    activated_at = models.DateTimeField(null=True, default=None)
    expired_at = models.DateField(null=True)
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
    def days_of_access(self):
        return self.old_days_of_access

    @days_of_access.setter
    def days_of_access(self, data):
        if self.activated_at is None:
            raise ValueError('activate at should not be None')
        self.old_days_of_access = data
        self.expired_at = (self.activated_at + timedelta(days=data)).date()

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


class UserSubscriptionsSummary:
    """
    This class provides summary data about user subscriptions.
    This is not a model, but a utility class to handle user subscriptions
    """

    def __init__(self, django_user_or_user_id):
        if isinstance(django_user_or_user_id, get_user_model()):
            self.user = django_user_or_user_id
            self.user_id = django_user_or_user_id.id
        else:
            self.user = None
            self.user_id = django_user_or_user_id

    def has_active_subscriptions(self):
        return self.active_subscriptions().exists()

    def active_subscriptions(self):
        return Subscription.objects.filter(
            subscriber_id=self.user_id, status=Subscription.Status.ACTIVE
        )

    @classmethod
    def users_with_active_subscriptions(cls):
        """
        Returns query set with user with at least one active subscription
        :return: Django Use Query Set
        """
        return get_user_model().objects.filter(
            subscriptions__status=Subscription.Status.ACTIVE
        ).order_by('-id').distinct()

    def memberkit_user_ids(self) -> set[int]:
        return set(Subscription.objects.filter(
            subscriber_id=self.user_id
        ).values_list('memberkit_user_id', flat=True))
