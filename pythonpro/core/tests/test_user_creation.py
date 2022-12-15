from pythonpro.core import facade


def test_user_with_default_password(db, settings):
    settings.DEFAULT_USER_CREATION_PASSWORD = 'mudar-senha'
    user = facade.register_lead('Renzo', 'renzo@dev.pro.br', 'google')
    assert user.check_password(settings.DEFAULT_USER_CREATION_PASSWORD)
