import pytest
from django.test import TestCase


@pytest.fixture
def dj_test_case():
    """Fixture to give access to Django's TestCase object"""
    return TestCase()


@pytest.fixture
def dj_assert_contains(dj_test_case: TestCase):
    """Fixture to expose Django's TestCase assertContains as a function"""
    return dj_test_case.assertContains


@pytest.fixture
def dj_assert_template_used(dj_test_case: TestCase):
    """Fixture to expose Django's TestCase assertContains as a function"""
    return dj_test_case.assertTemplateUsed
