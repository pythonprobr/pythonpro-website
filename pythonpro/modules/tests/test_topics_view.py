import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains, dj_assert_template_used
from pythonpro.memberkit.models import Subscription
from pythonpro.modules.models import Chapter, Module, Section, Topic


@pytest.fixture
def module(db):
    return baker.make(Module, slug='python-birds')


@pytest.fixture
def section(module):
    return baker.make(Section, module=module)


@pytest.fixture
def chapter(section):
    return baker.make(Chapter, section=section)


@pytest.fixture
def topics(chapter):
    return baker.make(Topic, 2, chapter=chapter)


@pytest.fixture
def topic(chapter):
    return baker.make(Topic, chapter=chapter, memberkit_url='https://memberkit.com.br')


@pytest.fixture
def resp_chapter(client_with_all_roles, chapter, topics):
    return client_with_all_roles.get(reverse(
        'modules:chapter_detail',
        kwargs={'chapter_slug': chapter.slug, 'module_slug': chapter.slug})
    )


def test_topic_title_on_chapter(resp_chapter, topics):
    for topic in topics:
        dj_assert_contains(resp_chapter, topic.title)


def test_topic_url_on_section(resp_chapter, topics):
    for topic in topics:
        dj_assert_contains(resp_chapter, topic.get_absolute_url())


@pytest.fixture
def resp_old_path(client_with_all_roles, topic, django_user_model):
    return client_with_all_roles.get(reverse('topics:detail_old', kwargs={'slug': topic.slug}))


def test_redirect_status_code(resp_old_path):
    assert resp_old_path.status_code == 301


def test_redirect_url(resp_old_path, topic):
    assert resp_old_path.url == topic.get_absolute_url()


@pytest.fixture
def resp_python_birds_user_without_subscription(client_with_user, topic, django_user_model):
    return client_with_user.get(
        reverse('modules:topic_detail', kwargs={'module_slug': topic.module_slug(), 'topic_slug': topic.slug})
    )


def test_success_status_code(resp_python_birds_user_without_subscription):
    assert resp_python_birds_user_without_subscription.status_code == 200


def test_video_template(resp_python_birds_user_without_subscription):
    dj_assert_template_used(resp_python_birds_user_without_subscription, 'topics/topic_detail.html')


def test_vimeo_video(resp_python_birds_user_without_subscription, topic):
    dj_assert_contains(resp_python_birds_user_without_subscription, f"'id': '{topic.vimeo_id}'")


@pytest.mark.parametrize('property_name', 'title description'.split())
def test_property_is_present(resp_python_birds_user_without_subscription, topic, property_name):
    dj_assert_contains(resp_python_birds_user_without_subscription, getattr(topic, property_name))


def test_breadcrumb_module(resp_python_birds_user_without_subscription, module):
    dj_assert_contains(
        resp_python_birds_user_without_subscription,
        f'<li class="breadcrumb-item"><a href="{module.get_absolute_url()}">{module.title}</a></li>'
    )


def test_breadcrumb_section(resp_python_birds_user_without_subscription, section):
    dj_assert_contains(
        resp_python_birds_user_without_subscription,
        f'<li class="breadcrumb-item"><a href="{section.get_absolute_url()}">{section.title}</a></li>'
    )


def test_breadcrumb_chapter(resp_python_birds_user_without_subscription, chapter):
    dj_assert_contains(
        resp_python_birds_user_without_subscription,
        f'<li class="breadcrumb-item"><a href="{chapter.get_absolute_url()}">{chapter.title}</a></li>'
    )


def test_breadcrumb_current(resp_python_birds_user_without_subscription, topic):
    dj_assert_contains(
        resp_python_birds_user_without_subscription,
        f'<li class="breadcrumb-item active" aria-current="page">{topic.title}</li>'
    )


def test_discourse_topic_id(resp_python_birds_user_without_subscription, topic):
    dj_assert_contains(resp_python_birds_user_without_subscription, f"topicId: {topic.discourse_topic_id}")


def test_discourse_url(resp_python_birds_user_without_subscription, topic):
    dj_assert_contains(resp_python_birds_user_without_subscription, f"discourseUrl: '{settings.DISCOURSE_BASE_URL}'")


def test_python_birds_user_not_migrated(client_with_user, topic, logged_user):
    baker.make(
        Subscription,
        subscriber=logged_user,
        activated_at=None,
        memberkit_user_id=None
    )
    resp = client_with_user.get(
        reverse('modules:topic_detail', kwargs={'module_slug': topic.module_slug(), 'topic_slug': topic.slug})
    )
    assert resp.status_code == 301
    assert resp.url == reverse('migrate_to_memberkit')


def test_python_birds_migrated_user(client_with_user, topic, logged_user):
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=logged_user,
        activated_at=timezone.now(),
        memberkit_user_id=1
    )
    resp = client_with_user.get(
        reverse('modules:topic_detail', kwargs={'module_slug': topic.module_slug(), 'topic_slug': topic.slug})
    )
    assert resp.status_code == 301
    assert resp.url == topic.memberkit_url


@pytest.fixture(params='pytools objetos-pythonicos python-para-pythonistas python-patterns'.split())
def advanced_module(db, request):
    slug = request.param
    return baker.make(Module, slug=slug)


@pytest.fixture
def advanced_section(advanced_module):
    return baker.make(Section, module=advanced_module)


@pytest.fixture
def advanced_chapter(advanced_section):
    return baker.make(Chapter, section=advanced_section)


@pytest.fixture
def advanced_topic(advanced_chapter):
    return baker.make(Topic, chapter=advanced_chapter)


@pytest.fixture
def resp_user_without_subscription(client_with_user, advanced_topic):
    return client_with_user.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': advanced_topic.module_slug(), 'topic_slug': advanced_topic.slug})
    )


def test_user_without_subscription_hitting_member_landing_page(resp_user_without_subscription):
    assert resp_user_without_subscription.status_code == 302
    assert resp_user_without_subscription.url == reverse('checkout:bootcamp_lp')
