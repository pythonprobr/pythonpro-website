from django.contrib.auth import get_user_model
from django.db import models


class DiscordUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.DO_NOTHING, primary_key=True)
    discord_id = models.CharField(max_length=64)
    discord_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.discord_email
