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

from pytest import Item, CallInfo, TestReport, Config

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
        #                   TEST PROPERTIES
        # ==========================================================
        self.__root_report_path : str = ""
        
        self.__filename         : str = ""
        self.__testfile_path    : str = ""
        self.__test_report_path : str = ""

        # -- Current test location properties ----------------------- #
        self.__relpath  : str = ""
        self.__lineno   : int = -1
        self.__testcase : str = ""

        # -- Current test info ---------------------------------- #
        self.__stage         : str = ""
        self.__testindex     : int = 1
        self.__fixture_names : list[str] = []
        self.__parameters    : dict = {}

        # -- Current test setup info -------------------------------- #
        self.__setup_start     : float = 0.0
        self.__setup_stop      : float = 0.0
        self.__setup_duration  : float = 0.0
        self.__setup_status    : str = "unknown"

        # -- Current test call info -------------------------------- #
        self.__call_start     : float = 0.0
        self.__call_stop      : float = 0.0
        self.__call_duration  : float = 0.0
        self.__call_status    : str = "unknown"

        # -- Current test teardown info ---------------------------- #
        self.__teardown_start     : float = 0.0
        self.__teardown_stop      : float = 0.0
        self.__teardown_duration  : float = 0.0
        self.__teardown_status    : str = "unknown"

        # -- Run logs ---------------------------------------------- #
        self.__setup_log    : str = ""
        self.__call_log     : str = ""
        self.__teardown_log : str = ""

        # self.__traceback = None

        self.__testinfo     : dict = {}

    @property
    def root_report_path(self) -> str:
        return self.__root_report_path

    @root_report_path.setter
    def root_report_path(self, path: str) -> None:
        self.__root_report_path = path

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
    def testfile_path(self) -> str:
        return self.__testfile_path

    @property
    def test_report_path(self) -> str:
        return self.__test_report_path
    
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

        # for key, value in config.option.__dict__.items():
        #     print(f"{key} = {value}")

    def _init_item(self, item: Item) -> None:
        self.__filename = item.fspath.basename
        self.__testfile_path = item.fspath.dirname
        
        self.__testindex = 0
        self.__relpath   = item.location[0]
        self.__lineno    = int( item.location[1] )
        self.__testcase  = item.originalname

        self.__fixture_names = getattr(item, "fixturenames", [])
        callspec : dict      = getattr(item, "callspec", {})
        self.__parameters    = getattr(callspec, "params", {})

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
    
    # def _update_report(self, item: Item, call: CallInfo) -> None:


    def print_properties(self) -> None:
        """Print all properties in a compact format."""
        props = {
            "🏠 Root Report Path": self.root_report_path,
            "📂 Test File Path": self.testfile_path,
            "📄 Test Report Path": self.test_report_path,
            "🔗 Relative Path": self.relpath,
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
            print(f"{key:<20}: {value}")
        
        print("=" * 50 + "\n")