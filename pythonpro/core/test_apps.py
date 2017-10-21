from pythonpro.core.apps import CoreConfig


def test_home():
    assert CoreConfig.name == 'core'
