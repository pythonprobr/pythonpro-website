import pytest
from django.conf import settings
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains, dj_assert_template_used
from pythonpro.modules.models import Chapter, Module, Section, Topic


@pytest.fixture
def module(db):
    return mommy.make(Module, slug='python-birds')


@pytest.fixture
def section(module):
    return mommy.make(Section, module=module)


@pytest.fixture
def chapter(section):
    return mommy.make(Chapter, section=section)


@pytest.fixture
def topics(chapter):
    return mommy.make(Topic, 2, chapter=chapter)


@pytest.fixture
def topic(chapter):
    return mommy.make(Topic, chapter=chapter)


@pytest.fixture
def resp_chapter(client_with_lead, django_user_model, chapter, topics):
    return client_with_lead.get(reverse(
        'modules:chapter_detail',
        kwargs={'chapter_slug': chapter.slug, 'module_slug': chapter.slug}),
        secure=True
    )


def test_topic_title_on_chapter(resp_chapter, topics):
    for topic in topics:
        dj_assert_contains(resp_chapter, topic.title)


def test_topic_url_on_section(resp_chapter, topics):
    for topic in topics:
        dj_assert_contains(resp_chapter, topic.get_absolute_url())


@pytest.fixture
def resp_old_path(client_with_lead, topic, django_user_model):
    return client_with_lead.get(
        reverse('topics:detail_old', kwargs={'slug': topic.slug}),
        secure=True)


def test_redirect_status_code(resp_old_path):
    assert resp_old_path.status_code == 301


def test_redirect_url(resp_old_path, topic):
    assert resp_old_path.url == topic.get_absolute_url()


@pytest.fixture
def resp(client_with_lead, topic, django_user_model):
    return client_with_lead.get(
        reverse('modules:topic_detail', kwargs={'module_slug': topic.module_slug(), 'topic_slug': topic.slug}),
        secure=True)


def test_success_status_code(resp):
    assert resp.status_code == 200


def test_video_template(resp):
    dj_assert_template_used(resp, 'topics/topic_detail.html')


def test_vimeo_video(resp, topic):
    dj_assert_contains(resp, f'<iframe id="topic-iframe" src="https://player.vimeo.com/video/{topic.vimeo_id}"')


@pytest.mark.parametrize('property_name', 'title description'.split())
def test_property_is_present(resp, topic, property_name):
    dj_assert_contains(resp, getattr(topic, property_name))


def test_breadcrumb_module(resp, module):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{module.get_absolute_url()}">{module.title}</a></li>'
    )


def test_breadcrumb_section(resp, section):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{section.get_absolute_url()}">{section.title}</a></li>'
    )


def test_breadcrumb_chapter(resp, chapter):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{chapter.get_absolute_url()}">{chapter.title}</a></li>'
    )


def test_breadcrumb_current(resp, topic):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item active" aria-current="page">{topic.title}</li>'
    )


@pytest.fixture
def module_member(db):
    return mommy.make(Module, slug='objetos-pythonicos')


@pytest.fixture
def section_member(module_member):
    return mommy.make(Section, module=module_member)


@pytest.fixture
def chapter_member(section_member):
    return mommy.make(Chapter, section=section_member)


@pytest.fixture
def topic_member(chapter_member):
    return mommy.make(Topic, chapter=chapter_member)


@pytest.fixture
def resp_lead_accessing_member_content(client_with_lead, topic_member, django_user_model, logged_user):
    return client_with_lead.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_member.module_slug(), 'topic_slug': topic_member.slug}),
        secure=True)


def test_lead_hitting_member_landing_page(resp_lead_accessing_member_content):
    assert resp_lead_accessing_member_content.status_code == 302
    assert resp_lead_accessing_member_content.url == reverse('member_landing_page')


@pytest.fixture
def resp_client_accessing_member_content(client_with_client, topic_member, django_user_model, mocker, logged_user):
    return client_with_client.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_member.module_slug(), 'topic_slug': topic_member.slug}),
        secure=True)


def test_client_hitting_member_landing_page(resp_client_accessing_member_content):
    assert resp_client_accessing_member_content.status_code == 302
    assert resp_client_accessing_member_content.url == reverse('member_landing_page')


@pytest.fixture
def resp_member_accessing_member_content(client_with_member, topic_member, django_user_model):
    return client_with_member.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_member.module_slug(), 'topic_slug': topic_member.slug}),
        secure=True)


def test_member_access_member_content(resp_member_accessing_member_content):
    dj_assert_template_used(resp_member_accessing_member_content, 'topics/topic_detail.html')


@pytest.fixture
def resp_member(client_with_member, topic, django_user_model):
    return client_with_member.get(
        reverse('modules:topic_detail', kwargs={'module_slug': topic.module_slug(), 'topic_slug': topic.slug}),
        secure=True)


def test_discourse_topic_id(resp_member, topic):
    dj_assert_contains(resp_member, f"topicId: {topic.discourse_topic_id}")


def test_discourse_url(resp_member, topic):
    dj_assert_contains(resp_member, f"discourseUrl: '{settings.DISCOURSE_BASE_URL}'")


@pytest.fixture
def module_client(db):
    return mommy.make(Module, slug='pytools')


@pytest.fixture
def section_client(module_client):
    return mommy.make(Section, module=module_client)


@pytest.fixture
def chapter_client(section_client):
    return mommy.make(Chapter, section=section_client)


@pytest.fixture
def topic_client(chapter_client):
    return mommy.make(Topic, chapter=chapter_client)


@pytest.fixture
def resp_lead_accesing_client_content(client_with_lead, topic_client, django_user_model, mocker, logged_user):
    return client_with_lead.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_client.module_slug(), 'topic_slug': topic_client.slug}),
        secure=True)


@pytest.fixture
def resp_client_accessing_client_content(client_with_client, topic_client, django_user_model, client_with_lead=None):
    return client_with_client.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_client.module_slug(), 'topic_slug': topic_client.slug}),
        secure=True)


def test_client_access_client_content(resp_client_accessing_client_content):
    dj_assert_template_used(resp_client_accessing_client_content, 'topics/topic_detail.html')


@pytest.fixture
def resp_member_accessing_client_content(client_with_member, topic_client, django_user_model):
    return client_with_member.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_client.module_slug(), 'topic_slug': topic_client.slug}),
        secure=True)


def test_member_access_client_content(resp_member_accessing_client_content):
    dj_assert_template_used(resp_member_accessing_client_content, 'topics/topic_detail.html')


@pytest.fixture
def module_webdev(db):
    return mommy.make(Module, slug='django')


@pytest.fixture
def section_webdev(module_webdev):
    return mommy.make(Section, module=module_webdev)


@pytest.fixture
def chapter_webdev(section_webdev):
    return mommy.make(Chapter, section=section_webdev)


@pytest.fixture
def topic_webdev(chapter_webdev):
    return mommy.make(Topic, chapter=chapter_webdev)


@pytest.fixture
def resp_lead_accesing_webdev_content(client_with_lead, topic_webdev, django_user_model, mocker, logged_user):
    return client_with_lead.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_webdev.module_slug(), 'topic_slug': topic_webdev.slug}),
        secure=True)


def test_lead_hitting_webdev_landing_page_oto(resp_lead_accesing_webdev_content):
    assert resp_lead_accesing_webdev_content.status_code == 302
    # TODO: Change after creating WebDev landing page
    assert resp_lead_accesing_webdev_content.url == reverse('checkout:membership_lp')


@pytest.fixture
def resp_client_accessing_webdev_content(client_with_client, topic_webdev, django_user_model, client_with_lead=None):
    return client_with_client.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_webdev.module_slug(), 'topic_slug': topic_webdev.slug}),
        secure=True)


def test_client_hitting_webdev_landing_page_oto(resp_client_accessing_webdev_content):
    assert resp_client_accessing_webdev_content.status_code == 302
    # TODO: Change after creating WebDev landing page
    assert resp_client_accessing_webdev_content.url == reverse('checkout:membership_lp')


@pytest.fixture
def resp_member_accessing_webdev_content(client_with_member, topic_webdev, django_user_model):
    return client_with_member.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_webdev.module_slug(), 'topic_slug': topic_webdev.slug}),
        secure=True)


def test_member_access_webdev_content(resp_member_accessing_webdev_content):
    dj_assert_template_used(resp_member_accessing_webdev_content, 'topics/topic_detail.html')


@pytest.fixture
def resp_webdev_accessing_webdev_content(client_with_webdev, topic_webdev, django_user_model):
    return client_with_webdev.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_webdev.module_slug(), 'topic_slug': topic_webdev.slug}),
        secure=True)


def test_webdev_access_webdev_content(resp_webdev_accessing_webdev_content):
    dj_assert_template_used(resp_webdev_accessing_webdev_content, 'topics/topic_detail.html')
