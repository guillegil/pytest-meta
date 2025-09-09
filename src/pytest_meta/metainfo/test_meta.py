import hashlib
import os
import time
from typing import Optional, Dict, Any, List
from pytest import Item, TestReport

from .models.test_models import TestRun, TestStats, StageResult, StageCapture

class TestMetadata:
    """Handles individual test metadata collection."""
    _last_test_id  : str = ''
    _last_test_idx : int = 0

    def __init__(self, *args, **kwargs):        
        # -- Test identification ---------------------------- #
        self.__id            : str = ""
        self.__nodeid        : str = ""
        self.__filename      : str = ""
        self.__testcase      : str = ""
        self.__relpath       : str = ""
        self.__abspath       : str = ""
        self.__lineno        : int = -1
        self.__hierarchy     : List[str] = []
        
        # -- Test execution context ------------------------ #
        self.__current_stage : str = ""
        self.__test_index    : int = 0
        self.__fixture_names : List[str] = []
        self.__parameters    : Dict[str, Any] = {}
        
        # -- Test timing and stats ----------------------- #
        self.__start_time    : Optional[float] = None
        self.__stop_time     : Optional[float] = None
        self.__stats         : TestStats = TestStats()
        
        # -- Current run data ----------------------------- #
        self.__current_run   : Optional[TestRun] = None
        self.__runs          : List[TestRun] = []
        
        # -- Current stage data --------------------------- #
        self.__current_stage_result : Optional[StageResult] = None
    
    # Properties for test identification
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def test_id(self) -> str:
        return self.id
    
    @property
    def nodeid(self) -> str:
        return self.__nodeid
    
    @property
    def filename(self) -> str:
        return self.__filename
    
    @property
    def testcase(self) -> str:
        return self.__testcase
    
    @property
    def relpath(self) -> str:
        return self.__relpath
    
    @property
    def abspath(self) -> str:
        return self.__abspath
    
    @property
    def lineno(self) -> int:
        return self.__lineno
    
    @property
    def hierarchy(self) -> List[str]:
        return self.__hierarchy.copy()
    
    # Properties for execution context
    @property
    def current_stage(self) -> str:
        return self.__current_stage
    
    @property
    def test_index(self) -> int:
        return self.__test_index
    
    @property
    def fixture_names(self) -> List[str]:
        return self.__fixture_names.copy()
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self.__parameters.copy()
    
    # Properties for timing and stats
    @property
    def start_time(self) -> Optional[float]:
        return self.__start_time
    
    @property
    def stop_time(self) -> Optional[float]:
        return self.__stop_time
    
    @property
    def duration(self) -> float:
        if self.__start_time is None:
            return 0.0
        end_time = self.__stop_time or time.time()
        return end_time - self.__start_time
    
    @property
    def stats(self) -> TestStats:
        return self.__stats
    
    @property
    def runs(self) -> List[TestRun]:
        return self.__runs.copy()
    
    @property
    def current_run(self) -> Optional[TestRun]:
        return self.__current_run
    
    def generate_id(self, relpath: str, testcase: str) -> str:
        id_string = f"{relpath}::{testcase}"
        return hashlib.sha1(id_string.encode("utf-8")).hexdigest()

    # Helper methods
    def __split_path(self, path: str) -> List[str]:
        """Split a file path into components."""
        parts = []
        while True:
            path, tail = os.path.split(path)
            if tail:
                parts.append(tail)
            else:
                if path:
                    parts.append(path)
                break
        return parts[::-1]
    
    def __is_error(self, report: TestReport) -> bool:
        """Determine if this is an error (not just a test failure)."""
        # Setup/teardown failures are always errors
        if report.when in ("setup", "teardown") and report.failed:
            return True
        
        # For call phase, distinguish runtime errors from assertion failures
        if report.when == "call" and report.failed:
            if not report.longrepr:
                return True
            
            longrepr_str = str(report.longrepr)
            lines = longrepr_str.strip().split('\n')
            last_line = lines[-1] if lines else ""
            
            if ": " in last_line:
                exception_type = last_line.split(": ")[-1].split()[0]
                return exception_type != "AssertionError"
            
            # Fallback: look for common error patterns
            error_patterns = ["NameError", "TypeError", "ValueError", 
                            "AttributeError", "ImportError", "ZeroDivisionError"]
            return any(pattern in longrepr_str for pattern in error_patterns)
        
        return False
    
    # Lifecycle methods
    def initialize_from_item(self, item: Item) -> None:
        """Initialize test metadata from pytest Item."""
        self.__filename  = item.fspath.basename
        self.__abspath   = item.fspath.dirname
        self.__nodeid    = item.nodeid
        self.__relpath   = item.location[0]
        self.__lineno    = int(item.location[1])
        self.__testcase  = item.originalname
        self.__hierarchy = self.__split_path(self.__relpath)
        
        self.__fixture_names = getattr(item, "fixturenames", [])
        callspec = getattr(item, "callspec", {})
        self.__parameters = getattr(callspec, "params", {})
        
        self.__id = self.generate_id(self.relpath, self.testcase)
        
        # Set start time on first initialization
        if self.__start_time is None:
            self.__start_time = time.time()
    
    def start_new_run(self) -> None:
        """Start a new test run."""

        if self.current_stage == 'setup' and self._last_test_id == self.id:
            self.__test_index += 1
        
        self._last_test_id = self.id
    
        self.__current_run = TestRun(parameters=self.__parameters.copy())
        self.__runs.append(self.__current_run)
        
        # -- Update stats ------------------------------------- #
        self.__stats = TestStats(
            total_runs      = self.__stats.total_runs + 1,
            total_passed    = self.__stats.total_passed,
            total_failed    = self.__stats.total_failed,
            total_skipped   = self.__stats.total_skipped,
            total_errors    = self.__stats.total_errors
        )
    
    def start_stage(self, stage: str) -> None:
        """Start a test stage (setup/call/teardown)."""
        if not self.__current_run:
            self.start_new_run()
        
        self.__current_stage = stage
        self.__current_stage_result = StageResult()
        
        # -- Set stage start time ------------------------------ #
        if self.__current_run.start_time == 0.0:
            self.__current_run.start_time = time.time()
    
    def finish_stage(self, report: TestReport) -> None:
        """Finish current stage with report data."""
        if not self.__current_stage_result or not self.__current_run:
            return
        
        # -- Update stage results -------------------------------------- #
        self.__current_stage_result.status      = report.outcome
        self.__current_stage_result.start_time  = report.start
        self.__current_stage_result.stop_time   = report.stop
        self.__current_stage_result.duration    = report.duration
        self.__current_stage_result.passed      = report.passed
        self.__current_stage_result.failed      = report.failed
        self.__current_stage_result.skipped     = report.skipped
        self.__current_stage_result.error       = self.__is_error(report)
        
        # -- Update capture data ---------------------------------------- #
        longrepr = getattr(report, 'longrepr', '')
        self.__current_stage_result.capture = StageCapture(
            stdout   = getattr(report, 'capstdout', ''),
            stderr   = getattr(report, 'capstderr', ''),
            log      = getattr(report, 'caplog', ''),
            longrepr = longrepr if longrepr is not None else ''
        )
        
        # Assign to appropriate stage in current run
        if self.__current_stage == "setup":
            self.__current_run.setup = self.__current_stage_result
        elif self.__current_stage == "call":
            self.__current_run.call = self.__current_stage_result
        elif self.__current_stage == "teardown":
            self.__current_run.teardown = self.__current_stage_result
        
        # Update run status and timing
        self.__update_run_status()
        self.__current_run.stop_time = time.time()
        self.__current_run.duration = (self.__current_run.stop_time - 
                                     self.__current_run.start_time)
        
        # Update overall stats on call stage
        if self.__current_stage == "call":
            self.__update_stats(report.outcome)
    
    def __update_run_status(self) -> None:
        """Update overall run status based on stage results."""
        if not self.__current_run:
            return
        
        # Priority: error > failed > skipped > passed
        if (self.__current_run.setup.error or 
            self.__current_run.call.error or 
            self.__current_run.teardown.error):
            self.__current_run.status = "error"
        elif (self.__current_run.setup.failed or 
              self.__current_run.call.failed or 
              self.__current_run.teardown.failed):
            self.__current_run.status = "failed"
        elif (self.__current_run.setup.skipped or 
              self.__current_run.call.skipped or 
              self.__current_run.teardown.skipped):
            self.__current_run.status = "skipped"
        else:
            self.__current_run.status = "passed"
    
    def __update_stats(self, outcome: str) -> None:
        """Update test statistics."""
        if outcome == "passed":
            self.__stats = TestStats(
                total_runs=self.__stats.total_runs,
                total_passed=self.__stats.total_passed + 1,
                total_failed=self.__stats.total_failed,
                total_skipped=self.__stats.total_skipped,
                total_errors=self.__stats.total_errors
            )
        elif outcome == "failed":
            self.__stats = TestStats(
                total_runs=self.__stats.total_runs,
                total_passed=self.__stats.total_passed,
                total_failed=self.__stats.total_failed + 1,
                total_skipped=self.__stats.total_skipped,
                total_errors=self.__stats.total_errors
            )
        elif outcome == "skipped":
            self.__stats = TestStats(
                total_runs=self.__stats.total_runs,
                total_passed=self.__stats.total_passed,
                total_failed=self.__stats.total_failed,
                total_skipped=self.__stats.total_skipped + 1,
                total_errors=self.__stats.total_errors
            )
    
    def finish_test(self) -> None:
        """Finish the entire test."""
        self.__stop_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            'id': self.id,
            'nodeid': self.nodeid,
            'filename': self.filename,
            'testcase': self.testcase,
            'relpath': self.relpath,
            'abspath': self.abspath,
            'lineno': self.lineno,
            'hierarchy': self.hierarchy,
            'fixture_names': self.fixture_names,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'duration': self.duration,
            'stats': {
                'total_runs': self.stats.total_runs,
                'total_passed': self.stats.total_passed,
                'total_failed': self.stats.total_failed,
                'total_skipped': self.stats.total_skipped,
                'total_errors': self.stats.total_errors,
            },
            'runs': [
                {
                    'parameters': run.parameters,
                    'status': run.status,
                    'start_time': run.start_time,
                    'stop_time': run.stop_time,
                    'duration': run.duration,
                    'setup': {
                        'status': run.setup.status,
                        'start_time': run.setup.start_time,
                        'stop_time': run.setup.stop_time,
                        'duration': run.setup.duration,
                        'passed': run.setup.passed,
                        'failed': run.setup.failed,
                        'skipped': run.setup.skipped,
                        'error': run.setup.error,
                        'capture': {
                            'stdout': run.setup.capture.stdout,
                            'stderr': run.setup.capture.stderr,
                            'log': run.setup.capture.log,
                            'longrepr': run.setup.capture.longrepr,
                        }
                    },
                    'call': {
                        'status': run.call.status,
                        'start_time': run.call.start_time,
                        'stop_time': run.call.stop_time,
                        'duration': run.call.duration,
                        'passed': run.call.passed,
                        'failed': run.call.failed,
                        'skipped': run.call.skipped,
                        'error': run.call.error,
                        'capture': {
                            'stdout': run.call.capture.stdout,
                            'stderr': run.call.capture.stderr,
                            'log': run.call.capture.log,
                            'longrepr': run.call.capture.longrepr,
                        }
                    },
                    'teardown': {
                        'status': run.teardown.status,
                        'start_time': run.teardown.start_time,
                        'stop_time': run.teardown.stop_time,
                        'duration': run.teardown.duration,
                        'passed': run.teardown.passed,
                        'failed': run.teardown.failed,
                        'skipped': run.teardown.skipped,
                        'error': run.teardown.error,
                        'capture': {
                            'stdout': run.teardown.capture.stdout,
                            'stderr': run.teardown.capture.stderr,
                            'log': run.teardown.capture.log,
                            'longrepr': run.teardown.capture.longrepr,
                        }
                    }
                } for run in self.runs
            ]
        }
    
    def __repr__(self) -> str:
        return (f"TestMetadata(id={self.id[:8]}..., testcase={self.testcase}, "
                f"runs={self.stats.total_runs}, duration={self.duration:.2f}s)")