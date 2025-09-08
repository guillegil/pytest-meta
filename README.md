# Pytest Meta

A powerful pytest plugin for collecting comprehensive metadata during test execution. Track session statistics, individual test details, timing information, and more with a simple, intuitive API.

## 🚀 Quick Start

### Installation
```bash
pip install pytest-meta
```

### Basic Usage
```python
from pytest_meta import meta

def test_example():
    # Access current test information
    print(f"Running test: {meta.testcase}")
    print(f"Test file: {meta.filename}")
    print(f"Current stage: {meta.current_stage}")

    # Access session statistics
    print(f"Total tests: {meta.total_tests}")
    print(f"Tests passed so far: {meta.total_passed}")

# Export metadata after test run
def pytest_sessionfinish():
    meta.export_json("test_results.json")
```

## 📊 API Reference

### Global Meta Instance

Import the global metadata collector:
```python
from pytest_meta import meta
```

### Session-Level Attributes

Access session-wide information and statistics:

| Attribute | Type | Description |
|-----------|------|-------------|
| `meta.session` | `SessionMetadata` | Full session metadata object |
| `meta.session_start_time` | `float \| None` | Unix timestamp when session started |
| `meta.session_duration` | `float` | Total session duration in seconds |
| `meta.total_tests` | `int` | Total number of tests collected |
| `meta.total_passed` | `int` | Number of tests that passed |
| `meta.total_failed` | `int` | Number of tests that failed |
| `meta.total_skipped` | `int` | Number of tests that were skipped |
| `meta.exitstatus` | `int \| None` | Session exit status (0 = success) |

#### Session Statistics Example
```python
def test_session_info():
    print(f"Session started at: {meta.session_start_time}")
    print(f"Running for: {meta.session_duration:.2f}s")
    print(f"Progress: {meta.total_passed}/{meta.total_tests} tests passed")
```

### Current Test Attributes

Access information about the currently running test:

| Attribute | Type | Description |
|-----------|------|-------------|
| `meta.current_test` | `TestMetadata` | Full current test metadata object |
| `meta.test_id` | `str` | Unique test identifier (SHA1 hash) |
| `meta.testcase` | `str` | Test function name |
| `meta.filename` | `str` | Test file basename |
| `meta.relpath` | `str` | Relative path to test file |
| `meta.lineno` | `int` | Line number where test is defined |
| `meta.current_stage` | `str` | Current execution stage (`setup`, `call`, `teardown`) |
| `meta.parameters` | `Dict[str, Any]` | Test parameters (for parametrized tests) |
| `meta.fixture_names` | `List[str]` | List of fixtures used by the test |

#### Current Test Example
```python
@pytest.mark.parametrize("value", [1, 2, 3])
def test_with_params(value):
    print(f"Test ID: {meta.test_id}")
    print(f"Test: {meta.testcase} in {meta.filename}:{meta.lineno}")
    print(f"Parameters: {meta.parameters}")
    print(f"Fixtures: {meta.fixture_names}")
    print(f"Stage: {meta.current_stage}")
```

### Test Query Methods

Find and filter tests by various criteria:

| Method | Return Type | Description |
|--------|-------------|-------------|
| `meta.get_test_by_id(test_id)` | `TestMetadata \| None` | Get test by unique ID |
| `meta.get_test_by_nodeid(nodeid)` | `TestMetadata \| None` | Get test by pytest nodeid |
| `meta.get_tests_by_filename(filename)` | `List[TestMetadata]` | Get all tests from a file |
| `meta.get_tests_by_status(status)` | `List[TestMetadata]` | Get tests with specific status |
| `meta.get_failed_tests()` | `List[TestMetadata]` | Get all failed tests |
| `meta.get_passed_tests()` | `List[TestMetadata]` | Get all passed tests |
| `meta.get_skipped_tests()` | `List[TestMetadata]` | Get all skipped tests |

#### Query Examples
```python
def test_query_examples():
    # Find specific test
    test = meta.get_test_by_nodeid("test_file.py::test_function")
    if test:
        print(f"Found test: {test.testcase}")

    # Get all tests from current file
    file_tests = meta.get_tests_by_filename(meta.filename)
    print(f"Tests in this file: {len(file_tests)}")

    # Check failed tests
    failed = meta.get_failed_tests()
    for test in failed:
        print(f"Failed: {test.testcase} - {test.runs[-1].call.capture.longrepr}")
```

### TestMetadata Object

Individual test metadata with detailed execution information:

#### Basic Properties
| Property | Type | Description |
|----------|------|-------------|
| `test.id` | `str` | Unique test identifier |
| `test.nodeid` | `str` | Pytest nodeid (e.g., `file.py::test_name`) |
| `test.testcase` | `str` | Test function name |
| `test.filename` | `str` | Test file basename |
| `test.relpath` | `str` | Relative path to test file |
| `test.abspath` | `str` | Absolute path to test directory |
| `test.lineno` | `int` | Line number of test definition |
| `test.hierarchy` | `List[str]` | File path components |

#### Execution Context
| Property | Type | Description |
|----------|------|-------------|
| `test.fixture_names` | `List[str]` | Fixtures used by the test |
| `test.parameters` | `Dict[str, Any]` | Parameters for parametrized tests |
| `test.current_stage` | `str` | Current execution stage |
| `test.test_index` | `int` | Run index (for multiple runs) |

#### Timing & Statistics
| Property | Type | Description |
|----------|------|-------------|
| `test.start_time` | `float \| None` | Test start timestamp |
| `test.stop_time` | `float \| None` | Test completion timestamp |
| `test.duration` | `float` | Total test duration |
| `test.stats` | `TestStats` | Test execution statistics |
| `test.runs` | `List[TestRun]` | All test runs (multiple for parametrized) |
| `test.current_run` | `TestRun \| None` | Currently executing run |

#### TestStats Object
| Property | Type | Description |
|----------|------|-------------|
| `stats.total_runs` | `int` | Total number of runs |
| `stats.total_passed` | `int` | Number of passed runs |
| `stats.total_failed` | `int` | Number of failed runs |
| `stats.total_skipped` | `int` | Number of skipped runs |
| `stats.total_errors` | `int` | Number of error runs |

#### TestRun Object
Each test run contains detailed stage information:

| Property | Type | Description |
|----------|------|-------------|
| `run.parameters` | `Dict[str, Any]` | Parameters for this run |
| `run.status` | `str` | Overall run status |
| `run.start_time` | `float` | Run start timestamp |
| `run.stop_time` | `float` | Run completion timestamp |
| `run.duration` | `float` | Run duration |
| `run.setup` | `StageResult` | Setup stage results |
| `run.call` | `StageResult` | Call stage results |
| `run.teardown` | `StageResult` | Teardown stage results |

#### StageResult Object
Detailed information for each test stage:

| Property | Type | Description |
|----------|------|-------------|
| `stage.status` | `str` | Stage outcome (`passed`, `failed`, `skipped`) |
| `stage.start_time` | `float` | Stage start timestamp |
| `stage.stop_time` | `float` | Stage completion timestamp |
| `stage.duration` | `float` | Stage duration |
| `stage.passed` | `bool` | Whether stage passed |
| `stage.failed` | `bool` | Whether stage failed |
| `stage.skipped` | `bool` | Whether stage was skipped |
| `stage.error` | `bool` | Whether stage had an error |
| `stage.capture` | `StageCapture` | Captured output and errors |

#### StageCapture Object
Captured output from each stage:

| Property | Type | Description |
|----------|------|-------------|
| `capture.stdout` | `str` | Captured stdout |
| `capture.stderr` | `str` | Captured stderr |
| `capture.log` | `str` | Captured log output |
| `capture.longrepr` | `str` | Long representation of failures/errors |

### Export Methods

Export collected metadata in various formats:

| Method | Description |
|--------|-------------|
| `meta.to_dict()` | Convert all metadata to dictionary |
| `meta.export_json(path, indent=4)` | Export to JSON file |

#### Export Example
```python
def pytest_sessionfinish():
    # Export detailed JSON report
    meta.export_json("detailed_results.json", indent=2)

    # Or get dictionary for custom processing
    data = meta.to_dict()

    # Access session data
    session_data = data["session"]
    print(f"Session duration: {session_data['duration']:.2f}s")

    # Access individual test data
    for test_id, test_data in data["tests"].items():
        print(f"Test {test_data['testcase']}: {test_data['stats']['total_runs']} runs")
```

## 🔧 Advanced Usage

### Custom Test Analysis
```python
def analyze_test_performance():
    """Find slowest tests."""
    all_tests = list(meta.tests.values())
    slowest = sorted(all_tests, key=lambda t: t.duration, reverse=True)[:5]

    print("Slowest tests:")
    for test in slowest:
        print(f"  {test.testcase}: {test.duration:.2f}s")

def find_flaky_tests():
    """Find tests with inconsistent results."""
    flaky_tests = []
    for test in meta.tests.values():
        if test.stats.total_runs > 1:
            if test.stats.total_passed > 0 and test.stats.total_failed > 0:
                flaky_tests.append(test)

    print(f"Found {len(flaky_tests)} potentially flaky tests")
    return flaky_tests
```

### Real-time Monitoring
```python
def pytest_runtest_call(item):
    """Monitor test execution in real-time."""
    current = meta.current_test
    if current:
        print(f"Executing: {current.testcase}")
        print(f"  File: {current.filename}:{current.lineno}")
        print(f"  Parameters: {current.parameters}")

def pytest_runtest_logreport(report):
    """React to test results immediately."""
    if report.when == "call":
        if report.failed:
            print(f"❌ FAILED: {meta.testcase}")
            if meta.current_test and meta.current_test.current_run:
                error_msg = meta.current_test.current_run.call.capture.longrepr
                print(f"   Error: {error_msg[:100]}...")
        elif report.passed:
            print(f"✅ PASSED: {meta.testcase} ({report.duration:.2f}s)")
```

## 🎯 Possible Future Features

### 🔎 Enhanced Reporting
1. **HTML Report Generation**
   - **Idea**: Export MetaInfo.testinfo into a pretty HTML dashboard using Jinja2 templates.
   - **Value**: Rich view of test results (colors, expandable stacktraces, sortable tables).
   - **Demo Add-On**: add a `--meta-html=report.html` CLI option.

2. **Test Trend Analysis**
   - **Idea**: Store multiple JSON/DB snapshots of test runs and compare across runs.
   - **Value**: Spot flaky tests (sometimes pass, sometimes fail).
   - **Implementation**: Compare current run hash → past run results (per test ID).

3. **Failure Pattern Detection**
   - **Idea**: On failure, analyze stacktrace and classify the failure (assertion error, import error, timeout, etc.).
   - **Value**: Auto-group similar issues in the report ("10 tests failed due to ValueError").
   - **Implementation**: Extend the `__is_error` function into a category classifier.

4. **Coverage Integration**
   - **Idea**: If pytest-cov is installed, pull its coverage data and attach per-test coverage into meta.
   - **Value**: Show which tests cover which parts of the code → powerful debugging.

### 📊 Advanced Metadata

1. **Environment Info**
    - **Idea**: Record Python version, OS, CPU count, installed dependency versions.
    - **Implementation**: Use `platform`, `sys`, `pkg_resources`, `importlib.metadata`.
    - **Stored in**: `testinfo["environment"]`.

2. **Git Integration**
    - **Idea**: Store repo state: commit hash, branch, dirty/not.
    - **Implementation**: Simple `subprocess.run(["git", "rev-parse", "HEAD"])` or using `GitPython`.
    - **Value**: QA reports stay traceable to a commit/branch.

3. **Resource Usage**
   - **Idea**: Record per-test CPU, memory, or even network/file I/O usage.
   - **Implementation**: Use `psutil` around `pytest_runtest_call()`.
   - **Value**: Identify performance bottlenecks/tests that leak resources.

4. **Custom Markers Metadata**
   - **Idea**: Attach user-provided markers + tags + metadata (e.g., `@pytest.mark.issue("JIRA-123")`).
   - **Value**: Quick search/filtering by feature, ticket, component.

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.