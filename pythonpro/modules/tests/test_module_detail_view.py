import pytest
from django.core.management import call_command
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules import facade
from pythonpro.modules.models import Section, Module, Chapter


def generate_resp(slug, client):
    return client.get(reverse('modules:detail', kwargs={'slug': slug}))


@pytest.fixture
def modules(transactional_db):
    call_command('loaddata', 'pythonpro_modules.json')
    modules = facade.get_all_modules()
    return modules


@pytest.fixture
def client_with_user(client, django_user_model, modules):
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
        # reverse('modules:detail', kwargs={'slug': 'python-birds'}),

    ]

)
def test_page_content_with_pre_requisite(content, client_with_user):
    resp = generate_resp('objetos-pythonicos', client_with_user)
    dj_assert_contains(resp, content)


@pytest.fixture
def sections(python_birds):
    return mommy.make(Section, 2, module=python_birds)


@pytest.fixture
def python_birds(modules):
    return Module.objects.filter(slug='python-birds').get()


@pytest.fixture
def resp_with_sections(client_with_user, sections, python_birds):
    return client_with_user.get(reverse('modules:detail', kwargs={'slug': python_birds.slug}))


def test_section_titles(resp_with_sections, sections):
    for section in sections:
        dj_assert_contains(resp_with_sections, section.title)


def test_section_urls(resp_with_sections, sections):
    for section in sections:
        dj_assert_contains(resp_with_sections, section.get_absolute_url())


@pytest.fixture
def chapters(sections):
    result = []
    for section in sections:
        result.extend(mommy.make(Chapter, 2, section=section))
    return result


@pytest.fixture
def resp_with_chapters(client_with_user, python_birds, sections, chapters):
    return resp_with_sections(client_with_user, sections, python_birds)


def test_chapter_titles(resp_with_chapters, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_with_chapters, chapter.title)


def test_chapter_urls(resp_with_chapters, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_with_chapters, chapter.get_absolute_url())
