import pytest
from django.conf import settings
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains, dj_assert_template_used
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
    return baker.make(Topic, chapter=chapter)


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
def resp(client_with_all_roles, topic, django_user_model):
    return client_with_all_roles.get(
        reverse('modules:topic_detail', kwargs={'module_slug': topic.module_slug(), 'topic_slug': topic.slug})
    )


def test_success_status_code(resp):
    assert resp.status_code == 200


def test_video_template(resp):
    dj_assert_template_used(resp, 'topics/topic_detail.html')


def test_vimeo_video(resp, topic):
    dj_assert_contains(resp, f"'id': '{ topic.vimeo_id }'")


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


def test_discourse_topic_id(resp, topic):
    dj_assert_contains(resp, f"topicId: {topic.discourse_topic_id}")


def test_discourse_url(resp, topic):
    dj_assert_contains(resp, f"discourseUrl: '{settings.DISCOURSE_BASE_URL}'")


@pytest.fixture(params='objetos-pythonicos python-para-pythonistas python-patterns'.split())
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
def resp_not_advanced_user_accessing_advanced_content(client_with_not_advanced_roles, advanced_topic):
    return client_with_not_advanced_roles.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': advanced_topic.module_slug(), 'topic_slug': advanced_topic.slug})
    )


def test_not_advanced_user_hitting_member_landing_page(resp_not_advanced_user_accessing_advanced_content):
    assert resp_not_advanced_user_accessing_advanced_content.status_code == 302
    assert resp_not_advanced_user_accessing_advanced_content.url == reverse('checkout:bootcamp_lp')


@pytest.fixture
def resp_advanced_user_accessing_advanced_content(client_with_advanced_roles, advanced_topic):
    return client_with_advanced_roles.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': advanced_topic.module_slug(), 'topic_slug': advanced_topic.slug}),
    )


def test_advanced_user_access_advanced_content(resp_advanced_user_accessing_advanced_content):
    dj_assert_template_used(resp_advanced_user_accessing_advanced_content, 'topics/topic_detail.html')


@pytest.fixture
def level_one_module(db):
    return baker.make(Module, slug='pytools')


@pytest.fixture
def level_one_section(level_one_module):
    return baker.make(Section, module=level_one_module)


@pytest.fixture
def level_one_chapter(level_one_section):
    return baker.make(Chapter, section=level_one_section)


@pytest.fixture
def level_one_topic(level_one_chapter):
    return baker.make(Topic, chapter=level_one_chapter)


@pytest.fixture
def resp_not_level_one_user_accesing_level_one_content(client_with_not_level_one_roles, level_one_topic):
    return client_with_not_level_one_roles.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': level_one_topic.module_slug(), 'topic_slug': level_one_topic.slug})
    )


def test_not_level_one_user_accesing_level_one_content(resp_not_level_one_user_accesing_level_one_content):
    assert resp_not_level_one_user_accesing_level_one_content.status_code == 302
    assert resp_not_level_one_user_accesing_level_one_content.url == reverse('checkout:webdev_landing_page')


@pytest.fixture
def resp_level_one_user_accesing_level_one_content(client_with_level_one_roles, level_one_topic):
    return client_with_level_one_roles.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': level_one_topic.module_slug(), 'topic_slug': level_one_topic.slug}),
    )


def test_level_one_user_acces_level_one_content(resp_level_one_user_accesing_level_one_content):
    dj_assert_template_used(resp_level_one_user_accesing_level_one_content, 'topics/topic_detail.html')


@pytest.fixture(params='django entrevistas-tecnicas'.split())
def module_level_two(db, request):
    slug = request.param
    return baker.make(Module, slug=slug)


@pytest.fixture
def section_level_two(module_level_two):
    return baker.make(Section, module=module_level_two)


@pytest.fixture
def chapter_level_two(section_level_two):
    return baker.make(Chapter, section=section_level_two)


@pytest.fixture
def topic_level_two(chapter_level_two):
    return baker.make(Topic, chapter=chapter_level_two)


@pytest.fixture
def resp_not_level_two_accesing_level_two_content(client_with_not_level_two_roles, topic_level_two):
    return client_with_not_level_two_roles.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_level_two.module_slug(), 'topic_slug': topic_level_two.slug}),
    )


def test_not_level_two_hitting_webdev_landing_page_oto(resp_not_level_two_accesing_level_two_content):
    assert resp_not_level_two_accesing_level_two_content.status_code == 302
    assert resp_not_level_two_accesing_level_two_content.url == reverse('checkout:webdev_landing_page')


@pytest.fixture
def resp_level_two_accessing_webdev_content(client_with_level_two_roles, topic_level_two):
    return client_with_level_two_roles.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': topic_level_two.module_slug(), 'topic_slug': topic_level_two.slug}),
        secure=True)


def test_webdev_access_webdev_content(resp_level_two_accessing_webdev_content):
    dj_assert_template_used(resp_level_two_accessing_webdev_content, 'topics/topic_detail.html')


# @pytest.fixture
# def module_level_three(db):
#     return baker.make(Module, slug='entrevistas-tecnicas')
#
#
# @pytest.fixture
# def section_level_three(module_level_three):
#     return baker.make(Section, module=module_level_three)
#
#
# @pytest.fixture
# def chapter_level_three(section_level_three):
#     return baker.make(Chapter, section=section_level_three)
#
#
# @pytest.fixture
# def topic_level_three(chapter_level_three):
#     return baker.make(Topic, chapter=chapter_level_three)
#
#
# @pytest.fixture
# def resp_not_level_three_accesing_level_three_content(client_with_not_level_three_roles, topic_level_three):
#     return client_with_not_level_three_roles.get(
#         reverse('modules:topic_detail',
#                 kwargs={'module_slug': topic_level_three.module_slug(), 'topic_slug': topic_level_three.slug}),
#     )
#
#
# def test_not_level_three_hitting_level_three_landing_page(resp_not_level_three_accesing_level_three_content):
#     assert resp_not_level_three_accesing_level_three_content.status_code == 302
#     assert resp_not_level_three_accesing_level_three_content.url == reverse('checkout:bootcamp_lp')


# @pytest.fixture
# def resp_level_three_accessing_level_three_content(client_with_level_three_roles, topic_level_three):
#     return client_with_level_three_roles.get(
#         reverse('modules:topic_detail',
#                 kwargs={'module_slug': topic_level_three.module_slug(), 'topic_slug': topic_level_three.slug}),
#         secure=True)
#
#
# def test_level_three_access_level_three_content(resp_level_three_accessing_level_three_content):
#     dj_assert_template_used(resp_level_three_accessing_level_three_content, 'topics/topic_detail.html')
