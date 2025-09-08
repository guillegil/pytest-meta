from dataclasses import dataclass

@dataclass
class SessionStats:
    """Session statistics."""
    total_tests     : int = 0
    total_passed    : int = 0
    total_failed    : int = 0
    total_skipped   : int = 0
    total_errors    : int = 0