import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.courses.models import courses
from pythonpro.courses.models.courses import Course
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def resp(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return resp_not_logged(client)


@pytest.fixture
def resp_not_logged(client):
    return client.get(reverse('courses:index'))


courses_dec = pytest.mark.parametrize('course', courses.ALL.values())


def test_status_code_logged(resp):
    assert resp.status_code == 200


def test_status_code_not_logged(resp_not_logged):
    assert resp_not_logged.status_code == 200


def test_course_index_link_not_logged(resp_not_logged):
    """ Assert course index link is present when user is not logged """
    url = reverse('courses:index')
    dj_assert_contains(resp_not_logged, f'href="{url}"')


@courses_dec
def test_course_link_not_logged(course: Course, resp_not_logged):
    """ Assert course links are not present when user is not logged """
    dj_assert_not_contains(resp_not_logged, f'href="{course.url()}"')


def test_course_index_link_logged(resp):
    """ Assert course index link is not present when user is logged """
    url = reverse('courses:index')
    dj_assert_not_contains(resp, f'href="{url}"')


@courses_dec
def test_course_link_logged(course: Course, resp):
    """ Assert course links are present when user is logged """
    dj_assert_contains(resp, f'href="{course.url()}"')


@courses_dec
def test_anchor(course, resp_not_logged):
    dj_assert_contains(resp_not_logged, f'<h1 id="{course.slug}"')


@courses_dec
def test_title(course, resp_not_logged):
    dj_assert_contains(resp_not_logged, course.title)


@courses_dec
def test_objective(course: Course, resp_not_logged):
    dj_assert_contains(resp_not_logged, course.objective)


@courses_dec
def test_descritption(course: Course, resp_not_logged):
    dj_assert_contains(resp_not_logged, course.description)


@courses_dec
def test_target(course: Course, resp_not_logged):
    dj_assert_contains(resp_not_logged, course.target)
