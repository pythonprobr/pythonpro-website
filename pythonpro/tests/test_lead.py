from pythonpro import facade


def test_creation(db, django_user_model):
    user = facade.register_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads')
    assert django_user_model.objects.all().get() == user
