import pytest

from advanced_logger import log
from pytest_meta import meta

@pytest.mark.parametrize(
    "arg1,arg2",
    [
        (1,2),
        (3,4),
        (5,6),
    ]
)
@pytest.mark.parameters
def test_parameters(arg1, arg2):
    log.init_term_handler('myhandler', level=log.INFO)

    log.info(f'({meta.current_test.testcase}) {meta.current_test.test_index=}')


@pytest.mark.parametrize(
    "arg1,arg2",
    [
        (1,2),
        (3,4),
        (5,6),
    ]
)
@pytest.mark.parameters
def test_parameters_second(arg1, arg2, myconfig=True):
    log.init_term_handler('myhandler', level=log.INFO)

    log.info(f'({meta.current_test.fixture_names}')
    log.info(f'({meta.current_test.parameters}')
    log.info(f'({meta.current_test.testcase}) {meta.current_test.test_index=}')