import pytest

from pytest_meta import meta

@pytest.mark.full
@pytest.mark.parametrize('is_array', [(False), (True)])
def test_add_custom_trigger(is_array):
    meta.add_custom_meta('{id}.myvar', 'add_myvar', is_array=is_array)
    meta.trigger_event('add_myvar', data='This is my awaesome var 1')
    meta.trigger_event('add_myvar', data='This is my awaesome var 3')
    meta.trigger_event('add_myvar', data='This is my awaesome var 4')
    meta.trigger_event('add_myvar', data='This is my awaesome var 2')

    meta.set_custom_meta('tests.{id}.abspath', 'This is my wowo var')
