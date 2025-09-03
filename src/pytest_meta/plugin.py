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

from .metainfo.metainfo import meta

# ========== CONFIGURATION HOOKS ==========
@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser: Parser) -> None:
    """Add command-line options."""
    parser.addoption(
        "--reports", 
        action="store", 
        default="./",
        help="Specify the root directory for the reports path"
    )

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: Config) -> None:
    """Called after command line options have been parsed."""
    print("Setting the object meta")
    meta._set_pytest_config(config)

@pytest.hookimpl(tryfirst=True)
def pytest_unconfigure(config: Config) -> None:
    """Called before test process is exited."""
    pass 

# ========== SESSION HOOKS ==========

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: Session) -> None:
    """Called after Session object has been created."""
    meta._set_session_start_time( time.time() )
    
@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    """Called after whole test run finished."""
    meta._update_sessionfinish(session, exitstatus)

# ========== COLLECTION HOOKS ==========

@pytest.hookimpl(tryfirst=True)
def pytest_collect_file(file_path: Path, parent: Collector) -> Optional[Collector]:
    """Create collector for the given path."""
    # Only collect .py files to reduce noise
    if file_path.suffix == '.py':
        pass 

    return None

@pytest.hookimpl(tryfirst=True)
def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Generate parametrized tests."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session: Session, config: Config, items: List[Item]) -> None:
    """Modify collected test items."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session: Session) -> None:
    """Called after collection is completed."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_itemcollected(item: Item) -> None:
    """Called when test item is collected."""
    pass

# ========== TEST EXECUTION HOOKS ==========
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]) -> Optional[bool]:
    """Perform the runtest protocol for a single test item."""
    meta._init_item(item)
    return None

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid: str, location: tuple) -> None:
    """Called at the start of running the runtest protocol."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logfinish(nodeid: str, location: tuple) -> None:
    """Called at the end of running the runtest protocol."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: Item) -> None:
    """Called to execute the test item setup."""
    meta._update_item(item, "setup")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item: Item) -> None:
    """Called to run the test."""
    meta._update_item(item, "call")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item: Item, nextitem: Optional[Item]) -> None:
    """Called to execute the test item teardown."""
    meta._update_item(item, "teardown")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item: Item, call: CallInfo) -> Optional[TestReport]:
    """Create test report for the given item and call."""
    return None 

# ========== FIXTURE HOOKS ==========
@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request) -> None:
    """Called before fixture setup."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_fixture_post_finalizer(fixturedef: FixtureDef, request) -> None:
    """Called after fixture finalizer."""
    pass

# ========== REPORTING HOOKS ==========
@pytest.hookimpl(tryfirst=True)
def pytest_report_header(config: Config, start_path: Path) -> Union[str, List[str]]:
    """Add information to test report header."""
    return None

@pytest.hookimpl(tryfirst=True)
def pytest_report_collectionfinish(config: Config, start_path: Path, items: List[Item]) -> Union[str, List[str]]:
    """Add information after collection finished."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report: TestReport, config: Config) -> Optional[tuple]:
    """Return result-category, shortletter and verbose word."""
    return None

@pytest.hookimpl(tryfirst=True)
def pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus: int, config: Config) -> None:
    """Add section to terminal summary reporting."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: TestReport) -> None:
    """Process test setup/call/teardown report."""
    meta._update_report(report)

# ========== ERROR/WARNING HOOKS ==========
@pytest.hookimpl(tryfirst=True)
def pytest_warning_recorded(warning_message: warnings.WarningMessage, when: str, nodeid: str, location: tuple) -> None:
    """Called when warning is recorded."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(node, call: CallInfo, report: TestReport) -> None:
    """Called when exception occurred and can be interacted with."""
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_internalerror(excrepr, excinfo) -> Optional[bool]:
    """Called for internal errors."""
    return None
