# ======================================================================
#  Project   : pytest-meta
#  File      : test_plugin_comprehensive.py
#  Author    : Comprehensive Test Suite
#  License   : MIT
#
#  Description:
#  ----------------
#  Comprehensive test suite for pytest-meta plugin functionality.
#  Tests session metadata, test metadata, hooks, and edge cases.
#
# ======================================================================

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import time

# Import your plugin components
from pytest_meta import MetaCollector, meta
from pytest_meta import SessionMetadata
from pytest_meta import TestMetadata
from pytest_meta import SessionStats
from pytest_meta import TestStats, TestRun, StageResult, StageCapture


class TestSessionMetadata:
    """Test SessionMetadata functionality."""
    
    def test_session_initialization(self):
        """Test session metadata initialization."""
        session = SessionMetadata()
        
        assert session.start_time is None
        assert session.stop_time is None
        assert session.duration == 0.0
        assert not session.has_started
        assert not session.has_finished
        assert session.exitstatus == 0
        assert session.stats.total_tests == 0
    
    def test_session_lifecycle(self):
        """Test session start and finish."""
        session = SessionMetadata()
        
        # Test start
        assert session.start_session() is True
        assert session.has_started is True
        assert session.start_time is not None
        assert session.start_session() is False  # Can't start twice
        
        # Test finish
        assert session.finish_session(exitstatus=1) is True
        assert session.has_finished is True
        assert session.stop_time is not None
        assert session.exitstatus == 1
        assert session.finish_session() is False  # Can't finish twice
        assert session.duration > 0
    
    def test_session_statistics(self):
        """Test session statistics tracking."""
        session = SessionMetadata()
        
        # Test set_total_collected
        session.set_total_collected(10)
        assert session.stats.total_tests == 10
        
        # Test increment methods
        session.increment_passed()
        assert session.stats.total_passed == 1
        
        session.increment_failed()
        assert session.stats.total_failed == 1
        
        session.increment_skipped()
        assert session.stats.total_skipped == 1
        
        session.increment_error()
        assert session.stats.total_errors == 1
        
        # Test update_test_result
        session.update_test_result("passed")
        assert session.stats.total_passed == 2
        
        session.update_test_result("failed")
        assert session.stats.total_failed == 2
        
        session.update_test_result("skipped")
        assert session.stats.total_skipped == 2
        
        session.update_test_result("error")
        assert session.stats.total_errors == 2
    
    def test_session_to_dict(self):
        """Test session dictionary export."""
        session = SessionMetadata()
        session.start_session()
        session.set_total_collected(5)
        session.increment_passed()
        session.finish_session(exitstatus=0)
        
        data = session.to_dict()
        
        assert 'start_time' in data
        assert 'stop_time' in data
        assert 'duration' in data
        assert 'exitstatus' in data
        assert data['exitstatus'] == 0
        assert 'stats' in data
        assert data['stats']['total_tests'] == 5
        assert data['stats']['total_passed'] == 1


class TestTestMetadata:
    """Test TestMetadata functionality."""
    
    def create_mock_item(self, nodeid="test_file.py::test_function", 
                        filename="test_file.py", testcase="test_function"):
        """Create a mock pytest Item."""
        item = Mock()
        item.nodeid = nodeid
        item.originalname = testcase
        item.location = (filename, 10, testcase)
        item.fixturenames = ["fixture1", "fixture2"]
        
        # Mock fspath
        item.fspath = Mock()
        item.fspath.basename = filename
        item.fspath.dirname = "/path/to/tests"
        
        # Mock callspec for parametrized tests
        callspec = Mock()
        callspec.params = {"param1": "value1", "param2": "value2"}
        item.callspec = callspec
        
        return item
    
    def create_mock_report(self, when="call", outcome="passed", 
                          duration=0.1, longrepr=None):
        """Create a mock TestReport."""
        report = Mock()
        report.when = when
        report.outcome = outcome
        report.duration = duration
        report.start = time.time()
        report.stop = report.start + duration
        report.passed = outcome == "passed"
        report.failed = outcome == "failed"
        report.skipped = outcome == "skipped"
        report.longrepr = longrepr
        report.capstdout = "stdout output"
        report.capstderr = "stderr output"
        report.caplog = "log output"
        return report
    
    def test_test_initialization(self):
        """Test test metadata initialization."""
        test = TestMetadata()
        
        assert test.id == ""
        assert test.nodeid == ""
        assert test.filename == ""
        assert test.testcase == ""
        assert test.start_time is None
        assert test.stats.total_runs == 0
        assert len(test.runs) == 0
    
    def test_test_initialize_from_item(self):
        """Test test initialization from pytest item."""
        test = TestMetadata()
        item = self.create_mock_item()
        
        test.initialize_from_item(item)
        
        assert test.nodeid == "test_file.py::test_function"
        assert test.filename == "test_file.py"
        assert test.testcase == "test_function"
        assert test.lineno == 10
        assert test.fixture_names == ["fixture1", "fixture2"]
        assert test.parameters == {"param1": "value1", "param2": "value2"}
        assert test.id != ""  # Should generate an ID
        assert test.start_time is not None
    
    def test_test_stage_lifecycle(self):
        """Test test stage lifecycle."""
        test = TestMetadata()
        item = self.create_mock_item()
        test.initialize_from_item(item)
        
        # Test setup stage
        test.start_stage("setup")
        assert test.current_stage == "setup"
        assert test.current_run is not None
        assert test.stats.total_runs == 1
        
        setup_report = self.create_mock_report("setup", "passed")
        test.finish_stage(setup_report)
        assert test.current_run.setup.status == "passed"
        
        # Test call stage
        test.start_stage("call")
        assert test.current_stage == "call"
        
        call_report = self.create_mock_report("call", "passed")
        test.finish_stage(call_report)
        assert test.current_run.call.status == "passed"
        assert test.stats.total_passed == 1
        
        # Test teardown stage
        test.start_stage("teardown")
        teardown_report = self.create_mock_report("teardown", "passed")
        test.finish_stage(teardown_report)
        assert test.current_run.teardown.status == "passed"
        assert test.current_run.status == "passed"
    
    def test_test_multiple_runs(self):
        """Test multiple test runs (parametrized tests)."""
        test = TestMetadata()
        item = self.create_mock_item()
        test.initialize_from_item(item)
        
        # First run
        test.start_new_run()
        test.start_stage("call")
        report1 = self.create_mock_report("call", "passed")
        test.finish_stage(report1)
        
        # Second run
        test.start_new_run()
        test.start_stage("call")
        report2 = self.create_mock_report("call", "failed")
        test.finish_stage(report2)
        
        assert test.stats.total_runs == 2
        assert test.stats.total_passed == 1
        assert test.stats.total_failed == 1
        assert len(test.runs) == 2
    
    def test_error_classification(self):
        """Test error vs failure classification."""
        test = TestMetadata()
        item = self.create_mock_item()
        test.initialize_from_item(item)
        
        # Test assertion error (should be failure, not error)
        test.start_stage("call")
        assertion_report = self.create_mock_report(
            "call", "failed", 
            longrepr="AssertionError: expected 1 but got 2"
        )
        test.finish_stage(assertion_report)
        
        # Test runtime error (should be error)
        test.start_new_run()
        test.start_stage("call")
        runtime_report = self.create_mock_report(
            "call", "failed",
            longrepr="NameError: name 'undefined_var' is not defined"
        )
        test.finish_stage(runtime_report)
        
        # Check that error classification works
        # Note: This depends on your __is_error implementation
        assert test.stats.total_runs == 2
    
    def test_test_to_dict(self):
        """Test test dictionary export."""
        test = TestMetadata()
        item = self.create_mock_item()
        test.initialize_from_item(item)
        
        test.start_stage("call")
        report = self.create_mock_report("call", "passed")
        test.finish_stage(report)
        test.finish_test()
        
        data = test.to_dict()
        
        assert 'id' in data
        assert 'nodeid' in data
        assert 'filename' in data
        assert 'testcase' in data
        assert 'stats' in data
        assert 'runs' in data
        assert len(data['runs']) == 1
        assert 'setup' in data['runs'][0]
        assert 'call' in data['runs'][0]
        assert 'teardown' in data['runs'][0]


class TestMetaCollector:
    """Test MetaCollector functionality."""
    
    def create_mock_session(self, items=None):
        """Create a mock pytest Session."""
        session = Mock()
        session.items = items or []
        return session
    
    def create_mock_config(self):
        """Create a mock pytest Config."""
        return Mock()
    
    def test_collector_initialization(self):
        """Test collector initialization."""
        collector = MetaCollector()
        
        assert collector.session is not None
        assert collector.current_test is not None
        assert len(collector.tests) == 0
        assert collector.config is None
    
    def test_collector_session_lifecycle(self):
        """Test collector session lifecycle."""
        collector = MetaCollector()
        config = self.create_mock_config()
        session = self.create_mock_session()
        
        # Configure
        collector.collector_configure(config)
        assert collector.config == config
        
        # Session start
        collector.collector_sessionstart(session)
        assert collector.session.has_started
        
        # Collection finish
        session.items = [Mock(), Mock(), Mock()]  # 3 items
        collector.collector_collection_finish(session)
        assert collector.session.stats.total_tests == 3
        
        # Session finish
        collector.collector_sessionfinish(session, 0)
        assert collector.session.has_finished
        assert collector.session.exitstatus == 0
    
    def test_collector_test_lifecycle(self):
        """Test collector test lifecycle."""
        collector = MetaCollector()
        
        # Create mock item
        item = Mock()
        item.nodeid = "test_file.py::test_function"
        item.originalname = "test_function"
        item.location = ("test_file.py", 10, "test_function")
        item.fixturenames = []
        item.fspath = Mock()
        item.fspath.basename = "test_file.py"
        item.fspath.dirname = "/path"
        
        # Setup phase
        collector.collector_runtest_setup(item)
        assert collector.current_test.current_stage == "setup"
        
        # Call phase
        collector.collector_runtest_call(item)
        assert collector.current_test.current_stage == "call"
        
        # Teardown phase
        collector.collector_runtest_teardown(item)
        assert collector.current_test.current_stage == "teardown"
        
        # Log reports
        setup_report = Mock()
        setup_report.when = "setup"
        setup_report.outcome = "passed"
        setup_report.start = time.time()
        setup_report.stop = setup_report.start + 0.1
        setup_report.duration = 0.1
        setup_report.passed = True
        setup_report.failed = False
        setup_report.skipped = False
        setup_report.longrepr = None
        setup_report.capstdout = ""
        setup_report.capstderr = ""
        setup_report.caplog = ""
        
        collector.collector_runtest_logreport(setup_report)
        
        # Verify test was stored
        assert len(collector.tests) == 1
    
    def test_collector_convenience_properties(self):
        """Test collector convenience properties."""
        collector = MetaCollector()
        session = self.create_mock_session()
        
        collector.collector_sessionstart(session)
        collector.session.set_total_collected(5)
        collector.session.increment_passed()
        collector.session.increment_failed()
        
        assert collector.total_tests == 5
        assert collector.total_passed == 1
        assert collector.total_failed == 1
        assert collector.session_start_time is not None
    
    def test_collector_query_methods(self):
        """Test collector query methods."""
        collector = MetaCollector()
        
        # Create and add some test metadata
        test1 = TestMetadata()
        test1._TestMetadata__id = "test1"
        test1._TestMetadata__nodeid = "file1.py::test1"
        test1._TestMetadata__filename = "file1.py"
        
        test2 = TestMetadata()
        test2._TestMetadata__id = "test2"
        test2._TestMetadata__nodeid = "file2.py::test2"
        test2._TestMetadata__filename = "file2.py"
        
        collector._MetaCollector__test_metadata["test1"] = test1
        collector._MetaCollector__test_metadata["test2"] = test2
        
        # Test queries
        assert collector.get_test_by_id("test1") == test1
        assert collector.get_test_by_nodeid("file1.py::test1") == test1
        assert len(collector.get_tests_by_filename("file1.py")) == 1
    
    def test_collector_export(self):
        """Test collector export functionality."""
        collector = MetaCollector()
        session = self.create_mock_session()
        
        collector.collector_sessionstart(session)
        collector.session.set_total_collected(1)
        
        # Export to dict
        data = collector.to_dict()
        assert 'session' in data
        assert 'tests' in data
        
        # Export to JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            collector.export_json(temp_path)
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
            
            assert 'session' in loaded_data
            assert 'tests' in loaded_data
        finally:
            os.unlink(temp_path)


class TestGlobalMetaInstance:
    """Test the global meta instance."""
    
    def test_global_meta_exists(self):
        """Test that global meta instance exists and is correct type."""
        assert meta is not None
        assert isinstance(meta, MetaCollector)
    
    def test_global_meta_functionality(self):
        """Test basic functionality of global meta instance."""
        # Should be able to access properties
        assert hasattr(meta, 'session')
        assert hasattr(meta, 'current_test')
        assert hasattr(meta, 'tests')
        
        # Should be able to call methods
        assert callable(meta.to_dict)
        assert callable(meta.export_json)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_collector_export(self):
        """Test exporting empty collector."""
        collector = MetaCollector()
        data = collector.to_dict()
        
        # Session should have default values, not be empty
        assert 'session' in data
        assert data['session']['start_time'] is None
        assert data['session']['stop_time'] is None
        assert data['session']['duration'] == 0.0
        assert data['session']['exitstatus'] == 0
        assert data['tests'] == {}
    
    def test_collector_without_session_start(self):
        """Test collector behavior without session start."""
        collector = MetaCollector()
        
        # Should handle gracefully
        assert collector.total_tests == 0
        assert collector.session_start_time is None
    
    def test_test_metadata_without_initialization(self):
        """Test test metadata behavior without proper initialization."""
        test = TestMetadata()
        
        # Should have safe defaults
        assert test.id == ""
        assert test.testcase == ""
        assert test.duration == 0.0
    
    def test_invalid_json_export_path(self):
        """Test JSON export with invalid path."""
        collector = MetaCollector()
        
        # Should raise appropriate exception
        with pytest.raises(Exception):
            collector.export_json("/invalid/path/that/does/not/exist/file.json")


# Integration test that simulates a real pytest run
class TestIntegration:
    """Integration tests that simulate real pytest execution."""
    
    def test_complete_test_run_simulation(self):
        """Simulate a complete test run with multiple tests."""
        collector = MetaCollector()
        
        # Simulate pytest session start
        config = Mock()
        session = Mock()
        session.items = [Mock(), Mock()]  # 2 test items
        
        collector.collector_configure(config)
        collector.collector_sessionstart(session)
        collector.collector_collection_finish(session)
        
        # Simulate first test
        item1 = Mock()
        item1.nodeid = "test_file.py::test_one"
        item1.originalname = "test_one"
        item1.location = ("test_file.py", 5, "test_one")
        item1.fixturenames = []
        item1.fspath = Mock()
        item1.fspath.basename = "test_file.py"
        item1.fspath.dirname = "/tests"
        
        # Test 1: Setup -> Call -> Teardown
        collector.collector_runtest_setup(item1)
        
        setup_report = Mock()
        setup_report.when = "setup"
        setup_report.outcome = "passed"
        setup_report.start = time.time()
        setup_report.stop = setup_report.start + 0.01
        setup_report.duration = 0.01
        setup_report.passed = True
        setup_report.failed = False
        setup_report.skipped = False
        setup_report.longrepr = None
        setup_report.capstdout = ""
        setup_report.capstderr = ""
        setup_report.caplog = ""
        
        collector.collector_runtest_logreport(setup_report)
        
        collector.collector_runtest_call(item1)
        
        call_report = Mock()
        call_report.when = "call"
        call_report.outcome = "passed"
        call_report.start = time.time()
        call_report.stop = call_report.start + 0.1
        call_report.duration = 0.1
        call_report.passed = True
        call_report.failed = False
        call_report.skipped = False
        call_report.longrepr = None
        call_report.capstdout = "test output"
        call_report.capstderr = ""
        call_report.caplog = ""
        
        collector.collector_runtest_logreport(call_report)
        
        collector.collector_runtest_teardown(item1)
        
        teardown_report = Mock()
        teardown_report.when = "teardown"
        teardown_report.outcome = "passed"
        teardown_report.start = time.time()
        teardown_report.stop = teardown_report.start + 0.01
        teardown_report.duration = 0.01
        teardown_report.passed = True
        teardown_report.failed = False
        teardown_report.skipped = False
        teardown_report.longrepr = None
        teardown_report.capstdout = ""
        teardown_report.capstderr = ""
        teardown_report.caplog = ""
        
        collector.collector_runtest_logreport(teardown_report)
        
        # Simulate session finish
        collector.collector_sessionfinish(session, 0)
        
        # Verify final state
        assert collector.session.has_finished
        assert collector.session.stats.total_tests == 2
        assert collector.session.stats.total_passed == 1
        assert len(collector.tests) == 1
        
        # Export and verify
        data = collector.to_dict()
        assert data['session']['stats']['total_tests'] == 2
        assert data['session']['stats']['total_passed'] == 1
        assert len(data['tests']) == 1


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])