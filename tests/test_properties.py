import pytest
from pytest_meta import meta


@pytest.mark.full
@pytest.mark.properties
@pytest.mark.parametrize('a,b,c', [(1,2,3), (4,5,6)])
def test_parameters(a: int, b: int, c: int):
    parameters = {"a": a, "b": b, "c": c}

    assert hasattr(meta, "parameters"), "Meta object does not has attribute 'parameters'"
    assert meta.parameters == parameters, "The parameters extracted from meta does not match the one given to the function"

@pytest.fixture
def stage_setup():
    assert meta.stage == "setup", f"Stage should be 'setup' in the setup fixture, got {meta.stage}"
    yield None
    assert meta.stage == "teardown", f"Stage should be 'teardown' in the setup fixture, got {meta.stage}"

@pytest.fixture(autouse=True)
def stage_setup_autouse():
    assert meta.stage == "setup", f"Stage should be 'setup' in the setup fixture, got {meta.stage}"
    yield None
    assert meta.stage == "teardown", f"Stage should be 'teardown' in the setup fixture, got {meta.stage}"

@pytest.fixture(scope="session")
def stage_setup_session():
    assert meta.stage == "setup", f"Stage should be 'setup' in the setup fixture, got {meta.stage}"
    yield None
    assert meta.stage == "teardown", f"Stage should be 'teardown' in the setup fixture, got {meta.stage}"

@pytest.fixture(scope="function")
def stage_setup_function():
    assert meta.stage == "setup", f"Stage should be 'setup' in the setup fixture, got {meta.stage}"
    yield None
    assert meta.stage == "teardown", f"Stage should be 'teardown' in the setup fixture, got {meta.stage}"

@pytest.mark.full
@pytest.mark.properties
def test_stage(
    stage_setup,
    stage_setup_session,
    stage_setup_function
):
    assert "stage_setup" in meta.fixture_names
    assert "stage_setup_autouse" in meta.fixture_names
    assert "stage_setup_session" in meta.fixture_names
    assert "stage_setup_function" in meta.fixture_names

    assert meta.stage == "call", f"Stage should be 'call' in the test function, got {meta.stage}"