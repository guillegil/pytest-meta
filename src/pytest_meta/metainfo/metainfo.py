# ======================================================================
#  Project   : pytest-meta
#  File      : metainfo.py
#  Author    : Guillermo Gil <guillegil@proton.me>
#  License   : MIT
#  Repository: https://github.com/guillegil/pytest-meta
#  Version   : 0.1.0
#
#  Description:
#  ----------------
#  This module defines the `MetaInfo` class, which collects and stores
#  metadata during pytest test runs. It handles:
#    - Configuration parsing (CLI args, pytest options)
#    - Tracking test case properties (file, line, parameters, fixtures)
#    - Recording setup, call, and teardown timings and logs
#    - Printing collected metadata in a human-readable format (TBD)
#
#  Notes:
#  ----------------
#  - It also can include in the future some pytest general configuration.
#  - Still need to define a structure for a JSON to be exported.
#  - Add support for traceback catch.
#
# ======================================================================

import hashlib
import json
from pathlib import Path
import time
from pytest import Item, CallInfo, TestReport, Config, Session
import warnings
import re

from .routes import FIXED_ROUTES

class InvalidRouteWarning(UserWarning):
    """Warning for routes that conflict with fixed attributes."""
    pass

class MetaInfo:

    def __init__(self):
        # ==========================================================
        #                   CONFIG PROPERTIES
        # ==========================================================
        self.__invocation_args  : dict = {}
        self.__quiet            : bool = False
        self.__verbose          : int  = 1
        self.__max_failures     : int  = 1
        self.__markexpr         : str  = ""
        self.__tbstyle          : str  = ""
        self.__capture          : str  = ""

        # ==========================================================
        #                  SESSION PROPERTIES
        # ==========================================================
        self.__start_time_started : bool = False

        self.__session_start     : float = 0.0
        self.__session_stop      : float = 0.0
        self.__session_duration  : float = 0.0
 
        self.__session_total_tests   : int = 0
        self.__session_total_passed  : int = 0
        self.__session_total_failed  : int = 0
        self.__session_total_skipped : int = 0

        self.__exitstatus : int = 0

        # ==========================================================
        #                   TEST PROPERTIES
        # ==========================================================
        self.__root_report_path : str = ""
        
        self.__filename         : str = ""
        self.__abspath          : str = ""
        self.__test_report_path : str = ""

        # -- Current test location properties ----------------------- #
        self.__relpath  : str = ""
        self.__lineno   : int = -1
        self.__testcase : str = ""

        # -- Current test info ---------------------------------- #
        self.__id            : str = ""
        self.__nodeid        : str = ""
        self.__stage         : str = ""
        self.__testindex     : int = 1
        self.__fixture_names : list[str] = []
        self.__parameters    : dict = {}

        # -- Current test stage report info -------------------------- #
        self.__stage_start      : float  = 0.0
        self.__stage_stop       : float  = 0.0
        self.__stage_duration   : float  = 0.0
        self.__stage_outcome    : str    = ""
        self.__stage_passed     : bool   = False
        self.__stage_failed     : bool   = False
        self.__stage_skipped    : bool   = False
        self.__stage_error      : bool   = False

        # -- Current test setup report info -------------------------- #
        self.__setup_start      : float  = 0.0
        self.__setup_stop       : float  = 0.0
        self.__setup_duration   : float  = 0.0
        self.__setup_outcome    : str    = ""
        self.__setup_passed     : bool   = False
        self.__setup_failed     : bool   = False
        self.__setup_skipped    : bool   = False
        self.__setup_error      : bool   = False

        # -- Current test call info -------------------------------- #
        self.__call_start      : float  = 0.0
        self.__call_stop       : float  = 0.0
        self.__call_duration   : float  = 0.0
        self.__call_outcome    : str    = ""
        self.__call_passed     : bool   = False
        self.__call_failed     : bool   = False
        self.__call_skipped    : bool   = False
        self.__call_error      : bool   = False

        # -- Current test teardown info ---------------------------- #
        self.__teardown_start      : float  = 0.0
        self.__teardown_stop       : float  = 0.0
        self.__teardown_duration   : float  = 0.0
        self.__teardown_outcome    : str    = ""
        self.__teardown_passed     : bool   = False
        self.__teardown_failed     : bool   = False
        self.__teardown_skipped    : bool   = False
        self.__teardown_error      : bool   = False

        # -- Run logs ---------------------------------------------- #
        self.__stage_capture : dict = {
            "stdout": "",
            "stderr": "",
            "log": "",
            "longrepr": "",
        }

        self.__setup_capture : dict = {
            "stdout": "",
            "stderr": "",
            "log": "",
            "longrepr": "",
        }

        self.__call_capture : dict = {
            "stdout": "",
            "stderr": "",
            "log": "",
            "longrepr": "",
        }

        self.__teardown_capture : dict = {
            "stdout": "",
            "stderr": "",
            "log": "",
            "longrepr": "",
        }

        self.__testinfo  : dict = {
            "session": {
                "invocation_args": {},
                "start_time": 0.0,
                "stop_time": 0.0,
                "duration": 0.0,

                "total_tests": 0,

                "total_passed": 0,
                "total_failed": 0,
                "total_skipped": 0,

                "exitstatus": -1
            },

            "tests": {},
        }

        self.__custom_event_handlers = {}
        self.__routes = {}

    @property
    def root_report_path(self) -> str:
        return self.__root_report_path

    @root_report_path.setter
    def root_report_path(self, path: str) -> None:
        self.__root_report_path = path

    @property
    def session_start(self) -> float:
        return self.__session_start

    @property
    def session_stop(self) -> float:
        return self.__session_stop

    @property
    def session_duration(self) -> float:
        return self.__session_duration

    @property
    def session_total_tests(self) -> int:
        return self.__session_total_tests

    @property
    def session_total_passed(self) -> int:
        return self.__session_total_passed

    @property
    def session_total_failed(self) -> int:
        return self.__session_total_failed

    @property
    def exitstatus(self) -> int:
        return self.__exitstatus

    @property
    def session_total_skipped(self) -> int:
        return self.__session_total_skipped

    @property
    def relpath(self) -> str:
        return self.__relpath
    
    @property
    def lineno(self) -> int:
        return self.__lineno

    @property
    def testcase(self) -> str:
        return self.__testcase

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def abspath(self) -> str:
        return self.__abspath

    @property
    def test_report_path(self) -> str:
        return self.__test_report_path

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
    def stage(self) -> str:
        return self.__stage

    @property
    def testindex(self) -> int:
        return self.__testindex

    @property
    def testinfo(self) -> dict:
        return self.__testinfo

    @property
    def fixture_names(self) -> list[str]:
        return self.__fixture_names
    
    @property
    def parameters(self) -> dict:
        return self.__parameters

    # -- Stage info properties ---------------------------------- #
    @property
    def stage_start(self) -> float:
        return self.__stage_start

    @property
    def stage_stop(self) -> float:
        return self.__stage_stop

    @property
    def stage_duration(self) -> float:
        return self.__stage_duration

    @property
    def stage_outcome(self) -> str:
        return self.__stage_outcome

    @property
    def stage_passed(self) -> bool:
        return self.__stage_passed

    @property
    def stage_failed(self) -> bool:
        return self.__stage_failed

    @property
    def stage_skipped(self) -> bool:
        return self.__stage_skipped

    @property
    def stage_error(self) -> bool:
        return self.__stage_error

    @property
    def stage_capture(self) -> dict:
        return self.__stage_capture


    # -- Current test setup report info properties -------------- #
    @property
    def setup_start(self) -> float:
        return self.__setup_start

    @property
    def setup_stop(self) -> float:
        return self.__setup_stop

    @property
    def setup_duration(self) -> float:
        return self.__setup_duration

    @property
    def setup_outcome(self) -> str:
        return self.__setup_outcome

    @property
    def setup_passed(self) -> bool:
        return self.__setup_passed

    @property
    def setup_failed(self) -> bool:
        return self.__setup_failed

    @property
    def setup_skipped(self) -> bool:
        return self.__setup_skipped

    @property
    def setup_error(self) -> bool:
        return self.__setup_error

    # -- Current test call info properties ---------------------- #
    @property
    def call_start(self) -> float:
        return self.__call_start

    @property
    def call_stop(self) -> float:
        return self.__call_stop

    @property
    def call_duration(self) -> float:
        return self.__call_duration

    @property
    def call_outcome(self) -> str:
        return self.__call_outcome

    @property
    def call_passed(self) -> bool:
        return self.__call_passed

    @property
    def call_failed(self) -> bool:
        return self.__call_failed

    @property
    def call_skipped(self) -> bool:
        return self.__call_skipped

    @property
    def call_error(self) -> bool:
        return self.__call_error

    # -- Current test teardown info properties ------------------ #
    @property
    def teardown_start(self) -> float:
        return self.__teardown_start

    @property
    def teardown_stop(self) -> float:
        return self.__teardown_stop

    @property
    def teardown_duration(self) -> float:
        return self.__teardown_duration

    @property
    def teardown_outcome(self) -> str:
        return self.__teardown_outcome

    @property
    def teardown_passed(self) -> bool:
        return self.__teardown_passed

    @property
    def teardown_failed(self) -> bool:
        return self.__teardown_failed

    @property
    def teardown_skipped(self) -> bool:
        return self.__teardown_skipped

    @property
    def teardown_error(self) -> bool:
        return self.__teardown_error

    # -- Run logs properties ------------------------------------ #
    @property
    def setup_capture(self) -> dict:
        return self.__setup_capture

    @property
    def call_capture(self) -> dict:
        return self.__call_capture

    @property
    def teardown_capture(self) -> dict:
        return self.__teardown_capture

    def _set_session_start_time(self, time: float) -> None:
        if not self.__start_time_started:
            self.__session_start = time

            # Prevent this method to be called by the user
            self.__start_time_started = True

    def __parse_cli_args_to_dict(self, args_list: tuple) -> dict:
        """Convert CLI args list to a key-value dictionary."""
        result = {}
        i = 0
        
        while i < len(args_list):
            arg = args_list[i]
            
            if arg.startswith('-'):
                # Handle --key=value format
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    result[key] = value
                else:
                    # Handle --key value format (next item is the value)
                    key = arg
                    # Check if next item exists and is not another flag
                    if i + 1 < len(args_list) and not args_list[i + 1].startswith('-'):
                        result[key] = args_list[i + 1]
                        i += 1  # Skip the value in next iteration
                    else:
                        # It's a boolean flag (no value)
                        result[key] = True
            else:
                # Positional arguments (test files/directories)
                if 'positional' not in result:
                    result['positional'] = []
                result['positional'].append(arg)
            
            i += 1
        
        return result

    def _set_pytest_config(self, config: Config) -> None:
        self.__args = config.args
        self.__invocation_args = self.__parse_cli_args_to_dict(config.invocation_params.args)
        self.__verbose = config.option.verbose
        self.__quiet = getattr(config.option, "quiet", False)
        self.__tbstyle = config.option.tbstyle
        self.__max_failures = config.option.maxfail
        self.__markexpr = config.option.markexpr

    def __init_testinfo(self) -> None:
        if self.id not in self.__testinfo['tests']:
            self.__testinfo['tests'][self.id] = {
                "relpath": self.relpath,
                "abspath": self.abspath,

                "hierarchy": [],

                "filename": self.filename,
                "testcase": self.testcase,
                "lineno": self.lineno,
                
                "start_time": 0.0,
                "stop_time": 0.0,
                "duration": 0.0,
                
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_skipped": 0,

                "runs": [],
            }


        self.__testinfo['tests'][self.id]['runs'].append(
            {
                "parameters": self.parameters,
                "status": "",
                "start_time": 0.0,
                "stop_time": 0.0,
                "duration": 0.0,

                "setup": {
                    "status": "",
                    "start_time": 0.0,
                    "stop_time": 0.0,
                    "duration": 0.0,

                    "capture": {
                        "stdout": "",
                        "stderr": "",
                        "log": "",
                        "longrepr": "",
                    },
                },

                "call": {
                    "status": "",
                    "start_time": 0.0,
                    "stop_time": 0.0,
                    "duration": 0.0,

                    "capture": {
                        "stdout": "",
                        "stderr": "",
                        "log": "",
                        "longrepr": "",
                    },
                },

                "teardown": {
                    "status": "",
                    "start_time": 0.0,
                    "stop_time": 0.0,
                    "duration": 0.0,

                    "capture": {
                        "stdout": "",
                        "stderr": "",
                        "log": "",
                        "longrepr": "",
                    },
                },
            }
        )
        
    def _init_item(self, item: Item) -> None:
        self.__filename = item.fspath.basename
        self.__abspath = item.fspath.dirname
        
        self.__nodeid    = item.nodeid

        self.__testindex = 0
        self.__relpath   = item.location[0]
        self.__lineno    = int( item.location[1] )
        self.__testcase  = item.originalname

        self.__fixture_names = getattr(item, "fixturenames", [])
        callspec : dict      = getattr(item, "callspec", {})
        self.__parameters    = getattr(callspec, "params", {})

        id_string : str = f"{self.relpath}::{self.testcase}"
        self.__id = hashlib.sha1(id_string.encode("utf-8")).hexdigest()

        self.__init_testinfo()

    def __update_item_setup(self, item: Item) -> None:
        # -- Update the testindex since it starts at 1 ---------- # 
        self.__testindex += 1

    def __update_item_call(self, item: Item) -> None:
        pass

    def __update_item_teardown(self, item: Item) -> None:
        pass

    def _update_item(
        self, 
        item: Item, 
        stage: str
    ):
        self.__stage = stage

        if stage == "setup":
            self.__update_item_setup(item)
        elif stage == "call":
            self.__update_item_call(item)
        elif stage == "teardown":
            self.__update_item_teardown(item)
        else:
            pass
        
        # if self.stage == "setup":
        #     self.print_properties()

    def __is_error(self, report: TestReport):
        """Determine if this is an error (not just a test failure)."""
        
        # Setup/teardown failures are always errors
        if report.when in ("setup", "teardown") and report.failed:
            return True
        
        # For call phase, distinguish runtime errors from assertion failures
        if report.when == "call" and report.failed:
            if not report.longrepr:
                return True
            
            longrepr_str = str(report.longrepr)
            
            # Check the last line which contains the exception type
            lines = longrepr_str.strip().split('\n')
            last_line = lines[-1] if lines else ""
            
            # If the last line contains the file:line info, it usually ends with the exception type
            if ": " in last_line:
                exception_type = last_line.split(": ")[-1].split()[0]  # Get first word after ":"
                return exception_type != "AssertionError"
            
            # Fallback: look for common error patterns
            error_patterns = ["NameError", "TypeError", "ValueError", "AttributeError", "ImportError", "ZeroDivisionError"]
            return any(pattern in longrepr_str for pattern in error_patterns)
        
        return False

    def __update_testinfo_run(self) -> None:
        overall_status = self.__testinfo['tests'][self.id]['runs'][-1]['status']

        if overall_status == "":
            overall_status = self.stage_outcome
        elif self.stage_outcome in ["failed", "error"]:
            overall_status = self.stage_outcome
        else:
            pass

        self.__testinfo['tests'][self.id]['runs'][-1]['status'] = overall_status
        self.__testinfo['tests'][self.id]['runs'][-1]['start_time'] = self.stage_start
        self.__testinfo['tests'][self.id]['runs'][-1]['stop_time'] = self.stage_stop
        self.__testinfo['tests'][self.id]['runs'][-1]['duration'] = self.stage_duration

        self.__testinfo['tests'][self.id]['runs'][-1][self.stage]['status'] = self.stage_outcome
        self.__testinfo['tests'][self.id]['runs'][-1][self.stage]['start_time'] = self.stage_start
        self.__testinfo['tests'][self.id]['runs'][-1][self.stage]['stop_time'] = self.stage_stop
        self.__testinfo['tests'][self.id]['runs'][-1][self.stage]['duration'] = self.stage_duration
        self.__testinfo['tests'][self.id]['runs'][-1][self.stage]['capture'] = self.stage_capture

        if self.stage == "setup":
            if self.__testinfo['tests'][self.id]["total_tests"] == 0:
                self.__testinfo['tests'][self.id]["start_time"] = time.time()

        if self.stage == "call":
            self.__session_total_tests   += 1
            self.__testinfo['tests'][self.id]["total_tests"] += 1

            if self.stage_outcome == "passed":
                self.__testinfo['tests'][self.id]["total_passed"] += 1
                self.__session_total_passed  += 1
            elif self.stage_outcome == "failed":
                self.__testinfo['tests'][self.id]["total_failed"] += 1
                self.__session_total_failed += 1
            elif self.stage_outcome == "skipped":
                self.__testinfo['tests'][self.id]["total_skipped"] += 1
                self.__session_total_skipped += 1
            else: 
                pass
        
        if self.stage == "teardown":
            self.__testinfo['tests'][self.id]["stop_time"] = time.time()
            duration = self.__testinfo['tests'][self.id]["stop_time"] - self.__testinfo['tests'][self.id]["start_time"]
            self.__testinfo['tests'][self.id]["duration"] = duration

    def __update_report_setup(self, report: TestReport) -> None:
        self.__setup_start    = report.start
        self.__setup_stop     = report.stop
        self.__setup_duration = report.duration

        self.__setup_outcome = report.outcome
        self.__setup_passed  = report.passed
        self.__setup_failed  = report.failed
        self.__setup_skipped = report.skipped
        self.__setup_error   = self.__is_error(report)

        longrepr = getattr(report, 'longrepr', '')

        self.__setup_capture = {
            "stdout": getattr(report, 'capstdout', ''),
            "stderr": getattr(report, 'capstderr', ''),
            "log": getattr(report, 'caplog', ''),
            "longrepr": longrepr if longrepr is not None else ''
        }

        self.__stage_start     = self.setup_start
        self.__stage_stop      = self.setup_stop
        self.__stage_duration  = self.setup_duration
        self.__stage_outcome   = self.setup_outcome
        self.__stage_passed    = self.setup_passed
        self.__stage_failed    = self.setup_failed
        self.__stage_skipped   = self.setup_skipped
        self.__stage_error     = self.setup_error
        self.__stage_capture   = self.setup_capture

    def __update_report_call(self, report: TestReport) -> None:
        self.__call_start    = report.start
        self.__call_stop     = report.stop
        self.__call_duration = report.duration

        self.__call_outcome = report.outcome
        self.__call_passed  = report.passed
        self.__call_failed  = report.failed
        self.__call_skipped = report.skipped
        self.__call_error   = self.__is_error(report)

        longrepr = getattr(report, 'longrepr', '')

        self.__call_capture = {
            "stdout": getattr(report, 'capstdout', ''),
            "stderr": getattr(report, 'capstderr', ''),
            "log": getattr(report, 'caplog', ''),
            "longrepr": longrepr if longrepr is not None else ''
        }
        self.__stage_start     = self.call_start
        self.__stage_stop      = self.call_stop
        self.__stage_duration  = self.call_duration
        self.__stage_outcome   = self.call_outcome
        self.__stage_passed    = self.call_passed
        self.__stage_failed    = self.call_failed
        self.__stage_skipped   = self.call_skipped
        self.__stage_error     = self.call_error
        self.__stage_capture   = self.call_capture

    def __update_report_teardown(self, report: TestReport) -> None:
        self.__teardown_start    = report.start
        self.__teardown_stop     = report.stop
        self.__teardown_duration = report.duration

        self.__teardown_outcome = report.outcome
        self.__teardown_passed  = report.passed
        self.__teardown_failed  = report.failed
        self.__teardown_skipped = report.skipped
        self.__teardown_error   = self.__is_error(report)

        longrepr = getattr(report, 'longrepr', '')

        self.__teardown_capture = {
            "stdout": getattr(report, 'capstdout', ''),
            "stderr": getattr(report, 'capstderr', ''),
            "log": getattr(report, 'caplog', ''),
            "longrepr": longrepr if longrepr is not None else ''
        }

        self.__stage_start     = self.teardown_start
        self.__stage_stop      = self.teardown_stop
        self.__stage_duration  = self.teardown_duration
        self.__stage_outcome   = self.teardown_outcome
        self.__stage_passed    = self.teardown_passed
        self.__stage_failed    = self.teardown_failed
        self.__stage_skipped   = self.teardown_skipped
        self.__stage_error     = self.teardown_error
        self.__stage_capture   = self.teardown_capture

    def _update_report(self, report: TestReport) -> None:

        if self.stage == "setup":
            self.__update_report_setup(report)
        elif self.stage == "call":
            self.__update_report_call(report)
        elif self.stage == "teardown":
            self.__update_report_teardown(report)
        else:
            pass

        self.__update_testinfo_run()

    def _update_sessionfinish(self, session: Session, exitstatus: int) -> None:
        self.__session_stop = time.time()
        self.__session_duration = self.session_stop - self.session_start

        self.__exitstatus = exitstatus

        self.__testinfo["session"]["start_time"] = self.session_start
        self.__testinfo["session"]["stop_time"] = self.session_stop
        self.__testinfo["session"]["duration"] = self.session_duration
        
        self.__testinfo["session"]["total_tests"] = self.session_total_tests
        self.__testinfo["session"]["total_passed"] = self.session_total_passed
        self.__testinfo["session"]["total_failed"] = self.session_total_failed
        self.__testinfo["session"]["total_skipped"] = self.session_total_skipped
        self.__testinfo["session"]["exitstatus"] = self.exitstatus

    def print_properties(self) -> None:
        """Print all properties in a compact format."""
        props = {
            "🏠 Root Report Path": self.root_report_path,
            "📂 Absolute Path": self.abspath,
            "📂 Relative Path": self.relpath,
            "📄 Test Report Path": self.test_report_path,
            "🔑 ID": self.id,
            "🔑 Node ID": self.nodeid,
            "📝 Filename": self.filename,
            "🧪 Test Case": self.testcase,
            "📍 Line Number": self.lineno,
            "⚙️ Stage": self.stage,
            "🔢 Test Index": self.testindex,
            "🔧 Fixture Names": self.fixture_names,
            "⚡ Parameters": self.parameters,
            "📊 Test Info Keys": list(self.testinfo.keys()) if self.testinfo else "(empty)"
        }
        
        print("\n" + "=" * 50)
        print("🎯 META INFO PROPERTIES")
        print("=" * 50)
        
        for key, value in props.items():
            print(f"{key:<25}: {value}")
        
        print("=" * 50 + "\n")

    def __route_is_allowed(self, route: str) -> bool:
        if route.startswith('{id}.') or route.startswith('{test_id}'):
            route = f'tests.{route}'
        
        return route not in FIXED_ROUTES

    def __parse_route(self, route: str) -> list[str]:
        if not self.__route_is_allowed(route):
            warnings.warn(
                f'Route "{route}" conflicts with fixed attribute and will be ignored. '
                f'Is this a mistake? Please change the route.',
                InvalidRouteWarning,
                stacklevel=4
            )
            
            return [] 
        placeholder_pattern = re.compile(r'\{([^}]+)\}')

        splitted_route = route.split('.')
        new_route_parts: list[str] = []

        for route_part in splitted_route:
            match = placeholder_pattern.search(route_part)
            if match:
                placeholder = match.group(1)
                
                if hasattr(self, placeholder):
                    if placeholder == 'testcase':
                        new_route_parts.append( self.id )
                    else:
                        new_route_parts.append( str(getattr(self, placeholder, '')) )
                else:
                    # -- Will ignore this route attribute ------------------------------ #
                    pass
            else:
                new_route_parts.append( str(route_part) )
        
        # -- If the user does not specify 'test' as first part of the route ------------ #
        # -- but it specifies the id --------------------------------------------------- #
        if new_route_parts[0] == self.id:
            new_route_parts.insert(0, "tests")

        return new_route_parts

    def __add_to_route(self, route: str, value: any) -> None:
        is_array = self.__routes.get(route, {}).get('is_array', False)

        routes: list[str] = self.__parse_route(route)

        if not routes:
            return

        current = self.__testinfo

        # Navigate through all but the last route part
        for route_part in routes[:-1]:
            if route_part not in current:
                current[route_part] = {}
            elif not isinstance(current[route_part], dict):
                # Overwrite non-dict values to ensure we can navigate
                current[route_part] = {}
            current = current[route_part]

        # -- Set the final value --------------------------------- #
        final_key = routes[-1]

        if is_array:
            if final_key in current and isinstance(current[final_key], list):
                current[final_key].append(value)
            else:
                current[final_key] = [value]
        else:
            current[final_key] = value

    def add_custom_meta(
        self, 
        route       : str, 
        on_event    : str,
        is_array    : bool = False, 
        value_func = None, 
        default_value = None
    ):
        if on_event not in self.__custom_event_handlers:
            self.__custom_event_handlers[on_event] = []
        
        self.__routes[route] = {
            'is_array': is_array
        }

        handler = {
            'route': route,
            'is_array': is_array,
            'value_func': value_func,
            'default_value': default_value,
        }
        
        self.__custom_event_handlers[on_event].append(handler)  

    def set_custom_meta(self, route: str, value):
        """
        Directly set custom metadata value (bypass events).
        
        Args:
            route: Path like 'session.custom.build_number' or 'tests.{test_id}.custom.tags'
            value: Value to set
        """
        self.__add_to_route(route, value)

    def trigger_event(self, event_name: str, data=None, **kwargs):
            """
            Trigger a custom event to collect metadata.
            
            Args:
                event_name: Name of the event to trigger
                data: Data to pass to value functions (can be dict or any value)
                **kwargs: Additional context data
            
            Examples:
                meta.trigger_event('myevent', data={'build': '1.2.3'})
                meta.trigger_event('register_myvar', test_id='current_test')
                meta.trigger_event('set_priority', data='high', test_id=meta.id)
            """
            if event_name not in self.__custom_event_handlers:
                return
            
            # Prepare context
            context = kwargs.copy()
            if data is not None:
                if isinstance(data, dict):
                    context.update(data)
                else:
                    context['data'] = data
            
            # Add current test context if available
            if hasattr(self, 'id') and self.id:
                context.setdefault('test_id', self.id)
            
            for handler in self.__custom_event_handlers[event_name]:
                try:
                    route = handler['route']
                    value_func = handler['value_func']
                    default_value = handler['default_value']
                
                    # Get value
                    if value_func:
                        value = value_func(context)
                    elif 'data' in context:
                        value = context['data']
                    else:
                        value = default_value
                    
                    # Set the value
                    self.__add_to_route(route, value)
                    
                except Exception as e:
                    pass

    def export_json(self, path: str, indent: int = 4, ensure_ascii: bool = False) -> None:

        file_path = Path(path)
            
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.testinfo, f, indent=indent, ensure_ascii=ensure_ascii, 
                        separators=(',', ': '))
        except (OSError, TypeError) as e:
            raise e


meta: MetaInfo = MetaInfo()