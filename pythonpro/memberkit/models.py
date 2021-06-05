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

# class Subscription(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now_add=True)
#     payment = models.OneToOneField('PagarmePayment', on_delete=models.DO_NOTHING, )
#     subscription_type = models.OneToOneField(SubscriptionType, null=False, on_delete=models.DO_NOTHING)
