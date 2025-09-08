import time
from typing import Optional, Dict, Any
from pytest import Config, Session

from .models.session_models import SessionStats


class SessionMetadata:
    """Handles session-level metadata collection (no thread-safety)."""
    
    def __init__(self, *args, **kwargs):        
        # -- Session timing ---------------------------------- #
        self.__start_time    : Optional[float] = None
        self.__stop_time     : Optional[float] = None
        self.__has_started   : bool = False
        self.__has_finished  : bool = False
        
        # -- Session statistics ------------------------------ #
        self.__stats = SessionStats()
        self.__exitstatus: int = 0
        

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
    def stats(self) -> SessionStats:
        return self.__stats
    
    @property
    def exitstatus(self) -> int:
        return self.__exitstatus
    
    @property
    def has_started(self) -> bool:
        return self.__has_started
    
    @property
    def has_finished(self) -> bool:
        return self.__has_finished
    

    def start_session(self) -> bool:
        if self.__has_started:
            return False
        
        self.__start_time = time.time()
        self.__has_started = True
        return True
    
    def finish_session(self, session: Optional[Session] = None, exitstatus: int = 0) -> bool:
        if self.__has_finished:
            return False
        
        self.__stop_time = time.time()
        self.__exitstatus = exitstatus
        self.__has_finished = True
        return True
    
    # Statistics update methods
    def set_total_collected(self, total: int) -> None:
        self.__stats = SessionStats(
            total_tests   = total,
            total_passed  = self.__stats.total_passed,
            total_failed  = self.__stats.total_failed,
            total_skipped = self.__stats.total_skipped,
            total_errors  = self.__stats.total_errors
        )

    # Add to SessionMetadata:
    def update_test_result(self, outcome: str) -> None:
        if outcome == "passed":
            self.increment_passed()
        elif outcome == "failed":
            self.increment_failed()
        elif outcome == "skipped":
            self.increment_skipped()
        else:  # error
            self.increment_error()

    def increment_test_count(self) -> None:
        self.__stats = SessionStats(
            total_tests   = self.__stats.total_tests + 1,
            total_passed  = self.__stats.total_passed,
            total_failed  = self.__stats.total_failed,
            total_skipped = self.__stats.total_skipped,
            total_errors  = self.__stats.total_errors
        )
    
    def increment_passed(self) -> None:
        self.__stats = SessionStats(
            total_tests   = self.__stats.total_tests,
            total_passed  = self.__stats.total_passed + 1,
            total_failed  = self.__stats.total_failed,
            total_skipped = self.__stats.total_skipped,
            total_errors  = self.__stats.total_errors
        )
    
    def increment_failed(self) -> None:
        self.__stats = SessionStats(
            total_tests   = self.__stats.total_tests,
            total_passed  = self.__stats.total_passed,
            total_failed  = self.__stats.total_failed + 1,
            total_skipped = self.__stats.total_skipped,
            total_errors  = self.__stats.total_errors
        )
    
    def increment_skipped(self) -> None:
        self.__stats = SessionStats(
            total_tests   = self.__stats.total_tests,
            total_passed  = self.__stats.total_passed,
            total_failed  = self.__stats.total_failed,
            total_skipped = self.__stats.total_skipped + 1,
            total_errors  = self.__stats.total_errors
        )
    
    def increment_error(self) -> None:
        self.__stats = SessionStats(
            total_tests   = self.__stats.total_tests,
            total_passed  = self.__stats.total_passed,
            total_failed  = self.__stats.total_failed,
            total_skipped = self.__stats.total_skipped,
            total_errors  = self.__stats.total_errors + 1
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'start_time'    : self.start_time,
            'stop_time'     : self.stop_time,
            'duration'      : self.duration,
            'exitstatus'    : self.exitstatus,
            'stats': {
                'total_tests'   : self.stats.total_tests,
                'total_passed'  : self.stats.total_passed,
                'total_failed'  : self.stats.total_failed,
                'total_skipped' : self.stats.total_skipped,
                'total_errors'  : self.stats.total_errors,
            },
        }

    def __repr__(self) -> str:
        return (f"SessionMetadata(started={self.has_started}, "
                f"finished={self.has_finished}, duration={self.duration:.2f}s, "
                f"tests={self.stats.total_tests})")