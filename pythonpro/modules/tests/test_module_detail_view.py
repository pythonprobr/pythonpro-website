import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Section, PYTHON_BIRDS


def generate_resp(slug, client):
    return client.get(reverse('modules:detail', kwargs={'slug': slug}))


@pytest.fixture
def client_with_user(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client


def test_status_code(client_with_user):
    resp = generate_resp('python-birds', client_with_user)
    assert resp.status_code == 200


@pytest.mark.parametrize(
    'content',
    [
        'Python Birds',
        'Introduzir programação Procedural e Orientação a Objetos em Python.',
        'Alunos com nenhuma ou pouca experiência.',
        'Nenhum pré-requisito.',
        'Durante o módulo será desenvolvida uma versão simplificada do jogo Angry Birds. Assim o aluno aprenderá os '
        'conceitos ao mesmo tempo em que implementa um projeto prático.'

    ]

)
def test_page_content_without_pre_requisite(content, client_with_user):
    resp = generate_resp('python-birds', client_with_user)
    dj_assert_contains(resp, content)


@pytest.mark.parametrize(
    'content',
    [
        'Objetos Pythônicos',
        'Aprofundar o conhecimento de Orientação a Objetos tendo em vista as peculiaridade do Python.',
        'Alunos que conhecem OO e estão começando com Python ou que já usam a linguagem no dia-a-dia, mas querem '
        'aperfeiçoar o modo pythônico de programar.',
        'Python Birds',
        'Aprofundamento no conhecimento da linguagem: tipagem dinâmica, protocolos versus interfaces, '
        'classes abstratas, herança múltipla e sobrecarga de operadores são alguns dos temas cobertos.',
        reverse('modules:detail', kwargs={'slug': 'python-birds'}),

    ]

)
def test_page_content_with_pre_requisite(content, client_with_user):
    resp = generate_resp('objetos-pythonicos', client_with_user)
    dj_assert_contains(resp, content)


@pytest.fixture
def sections(transactional_db):
    return mommy.make(Section, 2, _module_slug=PYTHON_BIRDS.slug)


@pytest.fixture
def resp_with_user(client_with_user, sections):
    return client_with_user.get(reverse('modules:detail', kwargs={'slug': PYTHON_BIRDS.slug}))


def test_sections_urls(resp_with_user, sections):
    for section in sections:
        dj_assert_contains(resp_with_user, section.get_absolute_url())
