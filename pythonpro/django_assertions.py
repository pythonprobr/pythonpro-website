'''
Module to expose Django's TestCase assertions as functions
'''
from django.test import TestCase

_dj_testcase = TestCase()

dj_assert_contains = _dj_testcase.assertContains
dj_assert_not_contains = _dj_testcase.assertNotContains
dj_assert_template_used = _dj_testcase.assertTemplateUsed
