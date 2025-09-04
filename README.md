# Pytest Meta

## Possible future features

### 🔎 Enhanced Reporting
1. HTML Report Generation
   - **Idea**: Export MetaInfo.testinfo into a pretty HTML dashboard using Jinja2 templates.
   - **Value**: Rich view of test results (colors, expandable stacktraces, sortable tables).
   - **Demo** Add-On: add a --meta-html=report.html CLI option.
  
2. Test Trend Analysis
   - **Idea**: Store multiple JSON/DB snapshots of test runs and compare across runs.
   - **Value**: Spot flaky tests (sometimes pass, sometimes fail).
   - **Implementation**: Compare current run hash → past run results (per test ID).
  
3. Failure Pattern Detection
   - **Idea**: On failure, analyze stacktrace and classify the failure (assertion error, import error, timeout, etc.).
   - **Value**: Auto-group similar issues in the report ("10 tests failed due to ValueError").
   - **Implementation**: Extend the __is_error function into a category classifier.

4. Coverage Integration
   - **Idea**: If pytest-cov is installed, pull its coverage data and attach per-test coverage into meta.
   - **Value**: Show which tests cover which parts of the code → powerful debugging.

### 📊 Advanced Metadata

1. Environment Info
    - **Idea**: Record Python version, OS, CPU count, installed dependency versions.
    - **Implementation**: Use `platform`, `sys`, `pkg_resources`, `importlib.metadata`.
    - **Stored in**: testinfo["environment"].

2. Git Integration
    - **Idea**: Store repo state: commit hash, branch, dirty/not.
    - **Implementation**: Simple `subprocess.run(["git", "rev-parse", "HEAD"])` or using `GitPython`.
    - **Value**: QA reports stay traceable to a commit/branch.

3. Resource Usage
   - **Idea**: Record per-test CPU, memory, or even network/file I/O usage.
   - **Implementation**: Use `psutil` around `pytest_runtest_call()`.
   - **Value**: Identify performance bottlenecks/tests that leak resources.

4. Custom Markers Metadata
   - **Idea**: Attach user-provided markers + tags + metadata (e.g., `@pytest.mark.issue("JIRA-123")`).
   - **Value**: Quick search/filtering by feature, ticket, component.