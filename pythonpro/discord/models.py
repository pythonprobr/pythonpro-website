from django.contrib.auth import get_user_model
from django.db import models


class DiscordUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.DO_NOTHING, primary_key=True)
    discord_id = models.CharField(max_length=64)
    discord_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='discord_created_at_desc_index'),
        ]

    def __str__(self):
        return self.discord_email


class DiscordLead(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'A', 'Ativa'
        INACTIVE = 'I', 'Inativa'

    discord_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.INACTIVE
    )
