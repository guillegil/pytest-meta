# ======================================================================
#  Project   : pytest-meta
#  File      : meta_collector.py
#  Author    : Guillermo Gil <guillegil@proton.me>
#  License   : MIT
#  Repository: https://github.com/guillegil/pytest-meta
#  Version   : 0.1.0
#
#  Description:
#  ----------------
#  Main coordinator class that orchestrates metadata collection during
#  pytest test runs. Manages SessionMetadata and TestMetadata instances,
#  implements pytest hooks, and provides the main API for metadata access.
#
# ======================================================================

import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from pytest import Item, TestReport, Config, Session

from .session_meta import SessionMetadata
from .test_meta import TestMetadata


class MetaCollector:
    """
    Main coordinator for pytest metadata collection.
    
    Orchestrates SessionMetadata and TestMetadata instances,
    implements pytest hooks, and provides unified API access.
    """
    
    def __init__(self):
        # Core metadata instances
        self.__session_metadata : SessionMetadata = SessionMetadata()
        self.__test_metadata    : Dict[str, TestMetadata] = {}
        self.__current_test     : TestMetadata = TestMetadata()
        self.__next_test        : TestMetadata = TestMetadata()
        
        # Configuration and state
        self.__config: Optional[Config] = None
        self.__session: Optional[Session] = None
        self.__root_report_path: str = ""
        
        # Collection tracking
        self.__collection_finished: bool = False
        self.__session_started: bool = False
    
    # ================================================================
    #                        PROPERTIES
    # ================================================================
    
    @property
    def session(self) -> Optional[SessionMetadata]:
        """Access to session metadata."""
        return self.__session_metadata
    
    @property
    def current_test(self) -> Optional[TestMetadata]:
        """Access to currently running test metadata."""
        return self.__current_test

    @property
    def next_test(self) -> Optional[TestMetadata]:
        """Access to next running test metadata."""
        return self.__next_test

    @property
    def tests(self) -> Dict[str, TestMetadata]:
        """Access to all test metadata instances."""
        return self.__test_metadata.copy()
    
    @property
    def config(self) -> Optional[Config]:
        """Access to pytest config."""
        return self.__config
    
    @property
    def root_report_path(self) -> str:
        """Root path for reports."""
        return self.__root_report_path
    
    @root_report_path.setter
    def root_report_path(self, path: str) -> None:
        """Set root report path."""
        self.__root_report_path = path
    

    # ================================================================
    #                     PYTEST HOOKS
    # ================================================================
    
    def collector_configure(self, config: Config) -> None:
        """Called after command line options have been parsed."""
        self.__config = config
    
    def collector_sessionstart(self, session: Session) -> None:
        """Called after the Session object has been created."""
        self.__session = session
        self.__session_metadata.start_session()
        self.__session_started = True
    
    def collector_collection_finish(self, session: Session) -> None:
        """Called after collection has been performed."""
        if self.__session_metadata:
            # Count collected items
            total_collected = len(session.items) if session.items else 0
            self.__session_metadata.set_total_collected(total_collected)
        self.__collection_finished = True
    
    def collector_runtest_protocol(self, item: Item, nextitem: Item) -> None:
        test_meta = self._get_or_create_test_metadata(item)
        test_meta.increment_test_index()
        self.__current_test = test_meta
        self.__next_test = TestMetadata().initialize_from_item(nextitem)

    def collector_runtest_setup(self, item: Item) -> None:
        """Called to perform the setup phase for a test item."""
        test_meta = self._get_or_create_test_metadata(item)
        test_meta.start_stage("setup")
        self.__current_test = test_meta
    
    def collector_runtest_call(self, item: Item) -> None:
        """Called to run the test for test item."""
        test_meta = self._get_or_create_test_metadata(item)
        test_meta.start_stage("call")
        self.__current_test = test_meta
    
    def collector_runtest_teardown(self, item: Item) -> None:
        """Called to perform the teardown phase for a test item."""
        test_meta = self._get_or_create_test_metadata(item)
        test_meta.start_stage("teardown")
        self.__current_test = test_meta
    
    def collector_runtest_logreport(self, report: TestReport) -> None:
        """Called after a test report has been created."""
        if self.__current_test:
            self.__current_test.finish_stage(report)
            
            # Update session stats on call phase
            if report.when == "call" and self.__session_metadata:
                self.__session_metadata.update_test_result(report.outcome)
            
            # Finish test after teardown
            if report.when == "teardown":
                self.__current_test.finish_test()
                self.__current_test = TestMetadata()
    
    def collector_sessionfinish(self, session: Session, exitstatus: int) -> None:
        """Called after whole test run finished."""
        if self.__session_metadata:
            self.__session_metadata.finish_session(session, exitstatus)
    
    # ================================================================
    #                    INTERNAL METHODS
    # ================================================================
    
    def _get_or_create_test_metadata(self, item: Item) -> TestMetadata:
        """Get existing or create new TestMetadata for an item."""
        # Generate test ID (same logic as in TestMetadata)
        temp_test = TestMetadata()
        temp_test.initialize_from_item(item)
        test_id = temp_test.id

        if test_id not in self.__test_metadata:
            self.__test_metadata[test_id] = temp_test
            test_meta = temp_test
        else:
            # Existing test (parametrized) - start a new run
            test_meta = self.__test_metadata[test_id]
            test_meta.update_from_item(item)
        
        return test_meta
    
    # ================================================================
    #                    PUBLIC API METHODS
    # ================================================================
    
    def get_test_by_id(self, test_id: str) -> Optional[TestMetadata]:
        """Get test metadata by ID."""
        return self.__test_metadata.get(test_id)
    
    def get_test_by_nodeid(self, nodeid: str) -> Optional[TestMetadata]:
        """Get test metadata by pytest nodeid."""
        for test_meta in self.__test_metadata.values():
            if test_meta.nodeid == nodeid:
                return test_meta
        return None
    
    def get_tests_by_filename(self, filename: str) -> List[TestMetadata]:
        """Get all tests from a specific file."""
        return [
            test_meta for test_meta in self.__test_metadata.values()
            if test_meta.filename == filename
        ]
    
    def get_tests_by_status(self, status: str) -> List[TestMetadata]:
        """Get all tests with a specific overall status."""
        result = []
        for test_meta in self.__test_metadata.values():
            # Check if any run has the specified status
            for run in test_meta.runs:
                if run.status == status:
                    result.append(test_meta)
                    break
        return result
    
    def get_failed_tests(self) -> List[TestMetadata]:
        """Get all tests that have failed runs."""
        return self.get_tests_by_status("failed")
    
    def get_passed_tests(self) -> List[TestMetadata]:
        """Get all tests that have passed runs."""
        return self.get_tests_by_status("passed")
    
    def get_skipped_tests(self) -> List[TestMetadata]:
        """Get all tests that have skipped runs."""
        return self.get_tests_by_status("skipped")
    
    # ================================================================
    #                    CONVENIENCE PROPERTIES
    # ================================================================
    
    # Delegate common session properties for backward compatibility
    @property
    def session_start_time(self) -> Optional[float]:
        """Session start time."""
        return self.__session_metadata.start_time if self.__session_metadata else None
    
    @property
    def session_duration(self) -> float:
        """Session duration."""
        return self.__session_metadata.duration if self.__session_metadata else 0.0
    
    @property
    def total_tests(self) -> int:
        """Total number of tests run."""
        return self.__session_metadata.stats.total_tests if self.__session_metadata else 0
    
    @property
    def total_passed(self) -> int:
        """Total number of passed tests."""
        return self.__session_metadata.stats.total_passed if self.__session_metadata else 0
    
    @property
    def total_failed(self) -> int:
        """Total number of failed tests."""
        return self.__session_metadata.stats.total_failed if self.__session_metadata else 0
    
    @property
    def total_skipped(self) -> int:
        """Total number of skipped tests."""
        return self.__session_metadata.stats.total_skipped if self.__session_metadata else 0
    
    @property
    def exitstatus(self) -> Optional[int]:
        """Session exit status."""
        return self.__session_metadata.exitstatus if self.__session_metadata else None
    
    # Delegate current test properties for backward compatibility
    @property
    def test_id(self) -> str:
        """Current test ID."""
        return self.__current_test.id if self.__current_test else ""
    
    @property
    def testcase(self) -> str:
        """Current test case name."""
        return self.__current_test.testcase if self.__current_test else ""
    
    @property
    def filename(self) -> str:
        """Current test filename."""
        return self.__current_test.filename if self.__current_test else ""
    
    @property
    def relpath(self) -> str:
        """Current test relative path."""
        return self.__current_test.relpath if self.__current_test else ""
    
    @property
    def lineno(self) -> int:
        """Current test line number."""
        return self.__current_test.lineno if self.__current_test else -1
    
    @property
    def current_stage(self) -> str:
        """Current test stage."""
        return self.__current_test.current_stage if self.__current_test else ""
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Current test parameters."""
        return self.__current_test.parameters if self.__current_test else {}
    
    @property
    def fixture_names(self) -> List[str]:
        """Current test fixture names."""
        return self.__current_test.fixture_names if self.__current_test else []
    
    # ================================================================
    #                    EXPORT METHODS
    # ================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all metadata to dictionary for JSON export."""
        result = {
            "session": self.__session_metadata.to_dict() if self.__session_metadata else {},
            "tests": {}
        }
        
        # Add all test metadata
        for test_id, test_meta in self.__test_metadata.items():
            result["tests"][test_id] = test_meta.to_dict()
        
        return result
    
    def export_json(self, path: str, indent: int = 4, ensure_ascii: bool = False) -> None:
        """Export all metadata to JSON file."""
        file_path = Path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=indent, ensure_ascii=ensure_ascii,
                         separators=(',', ': '))
        except (OSError, TypeError) as e:
            raise e
    
    def __repr__(self) -> str:
        session_info = f"session={self.__session_metadata is not None}"
        tests_info = f"tests={len(self.__test_metadata)}"
        current_info = f"current={self.__current_test.testcase if self.__current_test else None}"
        return f"MetaCollector({session_info}, {tests_info}, {current_info})"


# Global instance - this replaces the original `meta` global
meta: MetaCollector = MetaCollector()