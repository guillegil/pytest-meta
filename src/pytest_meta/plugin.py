import time
import pytest
from pytest import Item, CallInfo, TestReport, Config, Session
from _pytest.fixtures import FixtureDef
from _pytest.terminal import TerminalReporter
from _pytest.python import Metafunc
from _pytest.nodes import Collector
from _pytest.config.argparsing import Parser
from pathlib import Path
from typing import Any, List, Optional, Union
import warnings

from .metainfo.meta_collector import meta


class PytestHooksPlugin:
    """Pytest plugin with commonly available hooks."""
    
    def __init__(self):
        self.meta = meta
    
    # ========== CONFIGURATION HOOKS ==========
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_addoption(self, parser: Parser) -> None:
        """Add command-line options."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_configure(self, config: Config) -> None:
        """Called after command line options have been parsed."""
        self.meta.collector_configure(config)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_unconfigure(self, config: Config) -> None:
        """Called before test process is exited."""
        pass

    # ========== SESSION HOOKS ==========
    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionstart(self, session: Session) -> None:
        """Called after Session object has been created."""
        self.meta.collector_sessionstart(session)


    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionfinish(self, session: Session, exitstatus: int) -> None:
        """Called after whole test run finished."""
        self.meta.collector_sessionfinish(session, exitstatus)
    
    # ========== COLLECTION HOOKS ==========
    @pytest.hookimpl(tryfirst=True)
    def pytest_collect_file(self, file_path: Path, parent: Collector) -> Optional[Collector]:
        """Create collector for the given path."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_generate_tests(self, metafunc: Metafunc) -> None:
        """Generate parametrized tests."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session: Session, config: Config, items: List[Item]) -> None:
        """Modify collected test items."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_finish(self, session):
        """
        Called after collection has been performed.
        At this point, all parametrized test cases have been expanded.
        """
        self.meta.collector_collection_finish(session)
        # test_count_by_node = {}

        # for item in session.items:
        #     # item.nodeid looks like: "tests/test_file.py::test_case[param_set]"
        #     base_id = item.nodeid.split("[")[0]  # Strip param info
        #     test_count_by_node.setdefault(base_id, 0)
        #     test_count_by_node[base_id] += 1

        # print("\nCollected test counts:")
        # for node, count in test_count_by_node.items():
        #     print(f"{node} -> {count} tests")
        
    @pytest.hookimpl(tryfirst=True)
    def pytest_itemcollected(self, item: Item) -> None:
        """Called when test item is collected."""
        pass
    
    # ========== TEST EXECUTION HOOKS ==========
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_protocol(self, item: Item, nextitem: Optional[Item]) -> Optional[bool]:
        """Perform the runtest protocol for a single test item."""
        meta.collector_runtest_protocol(item, nextitem)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logstart(self, nodeid: str, location: tuple) -> None:
        """Called at the start of running the runtest protocol."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logfinish(self, nodeid: str, location: tuple) -> None:
        """Called at the end of running the runtest protocol."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_setup(self, item: Item) -> None:
        """Called to execute the test item setup."""
        self.meta.collector_runtest_setup(item)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_call(self, item: Item) -> None:
        """Called to run the test."""
        self.meta.collector_runtest_call(item)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_teardown(self, item: Item, nextitem: Optional[Item]) -> None:
        """Called to execute the test item teardown."""
        self.meta.collector_runtest_teardown(item)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_makereport(self, item: Item, call: CallInfo) -> Optional[TestReport]:
        """Create test report for the given item and call."""
        pass
    
    # ========== FIXTURE HOOKS ==========
    @pytest.hookimpl(tryfirst=True)
    def pytest_fixture_setup(self, fixturedef: FixtureDef, request) -> None:
        """Called before fixture setup."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_fixture_post_finalizer(self, fixturedef: FixtureDef, request) -> None:
        """Called after fixture finalizer."""
        pass
    
    # ========== REPORTING HOOKS ==========
    @pytest.hookimpl(tryfirst=True)
    def pytest_report_header(self, config: Config, start_path: Path) -> Union[str, List[str]]:
        """Add information to test report header."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_report_collectionfinish(self, config: Config, start_path: Path, items: List[Item]) -> Union[str, List[str]]:
        """Add information after collection finished."""
        pass

    @pytest.hookimpl(tryfirst=True)
    def pytest_report_teststatus(self, report: TestReport, config: Config) -> Optional[tuple]:
        """Return result-category, shortletter and verbose word."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_terminal_summary(self, terminalreporter: TerminalReporter, exitstatus: int, config: Config) -> None:
        """Add section to terminal summary reporting."""
        pass
    
    @pytest.hookimpl(trylast=True)
    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Process test setup/call/teardown report."""
        self.meta.collector_runtest_logreport(report)
    
    # ========== ERROR/WARNING HOOKS ==========
    @pytest.hookimpl(tryfirst=True)
    def pytest_warning_recorded(self, warning_message: warnings.WarningMessage, when: str, nodeid: str, location: tuple) -> None:
        """Called when warning is recorded."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(self, node, call: CallInfo, report: TestReport) -> None:
        """Called when exception occurred and can be interacted with."""
        pass
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(self, excrepr, excinfo) -> Optional[bool]:
        """Called for internal errors."""
        pass


# Plugin instance
pytest_hooks_plugin = PytestHooksPlugin()

# Register only the commonly available hooks
@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser): return pytest_hooks_plugin.pytest_addoption(parser)
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config): return pytest_hooks_plugin.pytest_configure(config)
@pytest.hookimpl(tryfirst=True)
def pytest_unconfigure(config): return pytest_hooks_plugin.pytest_unconfigure(config)
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session): return pytest_hooks_plugin.pytest_sessionstart(session)
@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus): return pytest_hooks_plugin.pytest_sessionfinish(session, exitstatus)
@pytest.hookimpl(tryfirst=True)
def pytest_collect_file(file_path, parent): return pytest_hooks_plugin.pytest_collect_file(file_path, parent)
@pytest.hookimpl(tryfirst=True)
def pytest_generate_tests(metafunc): return pytest_hooks_plugin.pytest_generate_tests(metafunc)
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items): return pytest_hooks_plugin.pytest_collection_modifyitems(session, config, items)
@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session): return pytest_hooks_plugin.pytest_collection_finish(session)
@pytest.hookimpl(tryfirst=True)
def pytest_itemcollected(item): return pytest_hooks_plugin.pytest_itemcollected(item)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem): return pytest_hooks_plugin.pytest_runtest_protocol(item, nextitem)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location): return pytest_hooks_plugin.pytest_runtest_logstart(nodeid, location)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logfinish(nodeid, location): return pytest_hooks_plugin.pytest_runtest_logfinish(nodeid, location)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item): return pytest_hooks_plugin.pytest_runtest_setup(item)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item): return pytest_hooks_plugin.pytest_runtest_call(item)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item, nextitem): return pytest_hooks_plugin.pytest_runtest_teardown(item, nextitem)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call): return pytest_hooks_plugin.pytest_runtest_makereport(item, call)
@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef, request): return pytest_hooks_plugin.pytest_fixture_setup(fixturedef, request)
@pytest.hookimpl(tryfirst=True)
def pytest_fixture_post_finalizer(fixturedef, request): return pytest_hooks_plugin.pytest_fixture_post_finalizer(fixturedef, request)
@pytest.hookimpl(tryfirst=True)
def pytest_report_header(config, start_path): return pytest_hooks_plugin.pytest_report_header(config, start_path)
@pytest.hookimpl(tryfirst=True)
def pytest_report_collectionfinish(config, start_path, items): return pytest_hooks_plugin.pytest_report_collectionfinish(config, start_path, items)
@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report, config): return pytest_hooks_plugin.pytest_report_teststatus(report, config)
@pytest.hookimpl(tryfirst=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config): return pytest_hooks_plugin.pytest_terminal_summary(terminalreporter, exitstatus, config)
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report): return pytest_hooks_plugin.pytest_runtest_logreport(report)
@pytest.hookimpl(tryfirst=True)
def pytest_warning_recorded(warning_message, when, nodeid, location): return pytest_hooks_plugin.pytest_warning_recorded(warning_message, when, nodeid, location)
@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(node, call, report): return pytest_hooks_plugin.pytest_exception_interact(node, call, report)
@pytest.hookimpl(tryfirst=True)
def pytest_internalerror(excrepr, excinfo): return pytest_hooks_plugin.pytest_internalerror(excrepr, excinfo)