import pytest
from django.conf import settings
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


def resp(client):
    return client.get(reverse('payments:options'))


@pytest.fixture
def resp_closed_subscriptions(settings, client):
    settings.SUBSCRIPTIONS_OPEN = False
    return resp(client)


@pytest.fixture
def resp_open_subscriptions(settings, client):
    settings.SUBSCRIPTIONS_OPEN = True
    return resp(client)


def test_status_code_subscriptions_closed(resp_closed_subscriptions):
    assert 200 == resp_closed_subscriptions.status_code


def test_status_code_subscriptions_open(resp_open_subscriptions):
    assert 200 == resp_open_subscriptions.status_code


@pytest.mark.parametrize(
    'content',
    [
        'R$ 1800,00',
        '10x de R$ 180,00 sem juros pelo pagseguro',
        'Parcelada sem Juros',
        'À Vista com Desconto',
        'Pague a vista por boleto e ganhe R$ 300,00 de desconto.',
        'com assunto "Inscrição" para receber um boleto no valor de R$1500,00.',
        'href="mailto:renzo@python.pro.br?subject=Inscrição%20Boleto"',

    ]
)
def test_content_subscription_open(content, resp_open_subscriptions):
    dj_assert_contains(resp_open_subscriptions, content)


def test_content_subscription_closed(resp_closed_subscriptions):
    dj_assert_contains(resp_closed_subscriptions, 'Inscrições Encerradas')


@pytest.mark.parametrize(
    'content',
    [
        '<form action="https://pagseguro.uol.com.br/pre-approvals/request.html" method="post">',
        f'<input type="hidden" name="code" value="{settings.PAGSEGURO_PAYMENT_PLAN}"/>',
        'name="submit"',

    ]
)
def test_pagseguro_form(content, resp_open_subscriptions):
    dj_assert_contains(resp_open_subscriptions, content)


@pytest.fixture
def thanks_resp(client):
    return client.get(reverse('payments:thanks'))


def test_thanks_status_code(thanks_resp):
    assert thanks_resp.status_code == 200
