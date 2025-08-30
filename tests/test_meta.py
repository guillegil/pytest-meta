import pytest
import pytest_meta
from pytest_meta import meta

@pytest.mark.full
@pytest.mark.meta
def test_meta():
    assert meta is not None, "The object meta is None"
    assert isinstance(meta, pytest_meta.MetaInfo), "The instance meta is not MetaInfo"


