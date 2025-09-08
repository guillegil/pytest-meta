from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class StageCapture:
    """Capture data for a test stage."""
    stdout   : str = ""
    stderr   : str = ""
    log      : str = ""
    longrepr : str = ""

@dataclass
class StageResult:
    """Result data for a test stage (setup/call/teardown)."""
    status      : str = ""
    start_time  : float = 0.0
    stop_time   : float = 0.0
    duration    : float = 0.0
    passed      : bool = False
    failed      : bool = False
    skipped     : bool = False
    error       : bool = False
    capture     : StageCapture = None
    
    def __post_init__(self):
        if self.capture is None:
            self.capture = StageCapture()

@dataclass
class TestRun:
    """Single test run (one execution with specific parameters)."""
    parameters  : Dict[str, Any] = None
    status      : str = ""
    start_time  : float = 0.0
    stop_time   : float = 0.0
    duration    : float = 0.0

    # -- Different stage results for each stage ----------------------- #
    setup       : StageResult = None
    call        : StageResult = None
    teardown    : StageResult = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.setup is None:
            self.setup = StageResult()
        if self.call is None:
            self.call = StageResult()
        if self.teardown is None:
            self.teardown = StageResult()

@dataclass
class TestStats:
    """Statistics for a test across all runs."""
    total_runs   : int = 0
    total_passed : int = 0
    total_failed : int = 0
    total_skipped: int = 0
    total_errors : int = 0