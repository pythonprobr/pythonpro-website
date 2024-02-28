from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.shortcuts import redirect, render

from pythonpro.memberkit import facade


@login_required
def migrate_to_memberkit(request):
    user = request.user
    facade.migrate_when_status_active(user)
    try:
        login_url = facade.create_login_url(user)
    except facade.InactiveUserException:
        mail_admins(
            f'Verificar migração de {user.email}',
            f'Link: https://painel.dev.pro.br/admin/memberkit/subscription/?q={user.email}'
        )
        return render(request, 'memberkit/manual_migration.html')
    else:
        return redirect(login_url)
