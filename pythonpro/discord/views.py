from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from pythonpro.discord.api_client import DiscordCredentials
from pythonpro.discord.models import DiscordUser
from pythonpro.memberkit.models import Subscription


@login_required
def autorize(request):
    # Obtendo token de acesso a endpoints via OAuth#2
    user = request.user
    has_discord_access = Subscription.objects.filter(
        subscriber=user,
        status=Subscription.Status.ACTIVE,
        subscription_types__has_discord_access=True
    ).exists()
    if has_discord_access:
        code = request.GET['code']
        autorize_uri = request.build_absolute_uri(reverse('discord:autorize'))
        member = add_user_to_discord_server(autorize_uri, code)
        discord_user_dict = member['user']
        DiscordUser(user=user, discord_id=discord_user_dict['id'], discord_email=discord_user_dict['email']).save()
        return redirect(f'https://discord.com/channels/{settings.DISCORD_GUILD_ID}')
    return render(request, 'discord/access_denied.html', status=403)


# Be careful when renaming, used on testing
def add_user_to_discord_server(autorize_uri, code):
    discord_credentials = DiscordCredentials(
        settings.DISCORD_APP_CLIENT_ID,
        settings.DISCORD_APP_CLIENT_SECRET,
        autorize_uri,
        settings.DISCORD_APP_BOT_TOKEN
    )
    api_app_client = discord_credentials.generate_api_client(code)
    # Adicionar o usuário em servidor do discord
    member = api_app_client.add_guild_member(guild_id=settings.DISCORD_GUILD_ID)
    return member
