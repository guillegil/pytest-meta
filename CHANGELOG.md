# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for custom metadata fields in test reports
- Configuration option to exclude certain test stages from reporting

### Changed

- Improved performance of metadata collection during test execution

### Fixed

- Fixed issue with fixture parameter parsing in parametrized tests

## [0.1.0] - 2025-08-30

### Added

- Initial release of pytest-meta plugin
- `MetaInfo` class for collecting test run metadata
- Support for tracking pytest configuration (CLI args, verbose mode, etc.)
- Test case property tracking (file path, line number, test name)
- Fixture names and parameter collection
- Setup, call, and teardown timing measurement
- Pretty-print functionality for debugging metadata
- Basic pytest plugin integration via entry points

### Technical Details

- Minimum Python 3.9+ support
- Compatible with pytest 7.0+
- MIT license

## [0.0.1] - 2025-08-25

### Added

- Project scaffolding and initial repository setup
- Basic `pyproject.toml` configuration
- README and license files

---

## Release Links

- [Unreleased]: https://github.com/guillegil/pytest-meta/compare/v0.1.0...HEAD
- [0.1.0]: https://github.com/guillegil/pytest-meta/releases/tag/v0.1.0
- [0.0.1]: https://github.com/guillegil/pytest-meta/releases/tag/v0.0.1
