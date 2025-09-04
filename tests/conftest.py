import pytest
from pytest_meta import meta

def pytest_runtest_logreport(report) -> None:
    meta.export_json('./reports/metainfo.json')