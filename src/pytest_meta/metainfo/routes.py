# routes.py

# List of "fixed" routes that CANNOT be overridden by users.
# These use placeholders {id} and {testindex} to represent dynamic values.
FIXED_ROUTES = [
    # -- Session-level fixed attributes ---------- #
    "session.invocation_args",
    "session.start_time",
    "session.stop_time",
    "session.duration",
    "session.total_tests",
    "session.total_passed",
    "session.total_failed",
    "session.total_skipped",
    "session.exitstatus",

    # ---- Test-level fixed attributes ----------- #
    "tests.{id}.relpath",
    "tests.{id}.abspath",
    "tests.{id}.hierarchy",
    "tests.{id}.filename",
    "tests.{id}.testcase",
    "tests.{id}.lineno",
    "tests.{id}.start_time",
    "tests.{id}.stop_time",
    "tests.{id}.duration",
    "tests.{id}.total_tests",
    "tests.{id}.total_passed",
    "tests.{id}.total_failed",
    "tests.{id}.total_skipped",
    "tests.{id}.runs",

    # ---- Run-level fixed attributes --------------- #
    "tests.{id}.runs.{testindex}.parameters",
    "tests.{id}.runs.{testindex}.status",
    "tests.{id}.runs.{testindex}.start_time",
    "tests.{id}.runs.{testindex}.stop_time",
    "tests.{id}.runs.{testindex}.duration",

    # ---- Stage-level fixed attributes -------------- #
    "tests.{id}.runs.{testindex}.setup",
    "tests.{id}.runs.{testindex}.call",
    "tests.{id}.runs.{testindex}.teardown",

    # ---- Capture objects --------------------------- #
    "tests.{id}.runs.{testindex}.setup.capture.stdout",
    "tests.{id}.runs.{testindex}.setup.capture.stderr",
    "tests.{id}.runs.{testindex}.setup.capture.log",
    "tests.{id}.runs.{testindex}.setup.capture.longrepr",

    "tests.{id}.runs.{testindex}.call.capture.stdout",
    "tests.{id}.runs.{testindex}.call.capture.stderr",
    "tests.{id}.runs.{testindex}.call.capture.log",
    "tests.{id}.runs.{testindex}.call.capture.longrepr",

    "tests.{id}.runs.{testindex}.teardown.capture.stdout",
    "tests.{id}.runs.{testindex}.teardown.capture.stderr",
    "tests.{id}.runs.{testindex}.teardown.capture.log",
    "tests.{id}.runs.{testindex}.teardown.capture.longrepr",
]