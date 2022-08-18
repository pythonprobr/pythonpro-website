from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Create your views here.
from django.urls import reverse

from pythonpro.discord.api_client import DiscordCredentials


@login_required
def autorize(request):
    # Obtendo token de acesso a endpoints via OAuth#2
    discord_credentials = DiscordCredentials(
        settings.DISCORD_APP_CLIENT_ID,
        settings.DISCORD_APP_CLIENT_SECRET,
        request.build_absolute_uri(reverse('discord:autorize')),
        settings.DISCORD_APP_BOT_TOKEN
    )

    api_app_client = discord_credentials.generate_api_client(request.GET['code'])

    # Adicionar o usuário em servidor do discord
    member = api_app_client.add_guild_member(guild_id=971162582624903288)

    return JsonResponse(member)
