import pytest
from django.core.management import call_command
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains, dj_assert_template_used
from pythonpro.modules import facade
from pythonpro.modules.models import Chapter, Module, Section


def generate_resp(slug, client):
    return client.get(reverse('modules:detail', kwargs={'slug': slug}))


@pytest.fixture
def modules(db):
    call_command('loaddata', 'pythonpro_modules.json')
    modules = facade.get_all_modules()
    return modules


def test_status_code(client_with_lead, modules):
    resp = generate_resp('python-birds', client_with_lead)
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
def test_lead_content(content, client_with_lead, modules):
    resp = generate_resp('python-birds', client_with_lead)
    dj_assert_contains(resp, content)


def test_lead_has_no_automation_button(client_with_lead, modules, python_birds):
    resp = generate_resp('python-birds', client_with_lead)
    dj_assert_not_contains(resp, reverse('modules:enrol', kwargs={'slug': python_birds.slug}))


def test_client_has_no_automation_button(client_with_client, modules, python_birds):
    resp = generate_resp('python-birds', client_with_client)
    dj_assert_contains(resp, reverse('modules:enrol', kwargs={'slug': python_birds.slug}))


def test_member_has_no_automation_button(client_with_member, modules, python_birds):
    resp = generate_resp('python-birds', client_with_member)
    dj_assert_contains(resp, reverse('modules:enrol', kwargs={'slug': python_birds.slug}))


@pytest.mark.parametrize(
    'content',
    [
        'Objetos Pythônicos',
        'Aprofundar o conhecimento de Orientação a Objetos tendo em vista as peculiaridade do Python.',
        'Alunos que conhecem OO e estão começando com Python ou que já usam a linguagem no dia-a-dia, mas querem '
        'aperfeiçoar o modo pythônico de programar.',
        'Aprofundamento no conhecimento da linguagem: tipagem dinâmica, protocolos versus interfaces, '
        'classes abstratas, herança múltipla e sobrecarga de operadores são alguns dos temas cobertos.',
        # reverse('modules:detail', kwargs={'slug': 'python-birds'}),

    ]

)
def test_member_content(content, client_with_member, modules):
    resp = generate_resp('objetos-pythonicos', client_with_member)
    dj_assert_contains(resp, content)


def test_client_content(client_with_client, modules):
    resp = generate_resp('pytools', client_with_client)
    dj_assert_template_used(resp, 'modules/module_detail.html')


def test_client_content_accesed_by_member(client_with_member, modules):
    resp = generate_resp('pytools', client_with_member)
    dj_assert_template_used(resp, 'modules/module_detail.html')


@pytest.fixture
def sections(python_birds):
    return baker.make(Section, 2, module=python_birds)


@pytest.fixture
def python_birds(modules):
    return Module.objects.filter(slug='python-birds').get()


@pytest.fixture
def resp_with_sections(client_with_lead, sections, python_birds):
    return _resp_with_sections(client_with_lead, sections, python_birds)


def _resp_with_sections(client_with_lead, sections, python_birds):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client_with_lead.get(reverse('modules:detail', kwargs={'slug': python_birds.slug}))


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
        result.extend(baker.make(Chapter, 2, section=section))
    return result


@pytest.fixture
def resp_with_chapters(client_with_lead, python_birds, sections, chapters):
    return _resp_with_sections(client_with_lead, sections, python_birds)


def test_chapter_titles(resp_with_chapters, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_with_chapters, chapter.title)


def test_chapter_urls(resp_with_chapters, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_with_chapters, chapter.get_absolute_url())


def test_enrol_user_tags(python_birds, client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.modules.modules_views.tag_as')
    resp = client_with_lead.get(reverse('modules:enrol', kwargs={'slug': python_birds.slug}))
    tag_as.assert_called_once_with(logged_user.email, logged_user.id, python_birds.slug)
    assert resp.status_code == 200
