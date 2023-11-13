from __future__ import annotations

import argparse
import os
import sys
from functools import wraps
from inspect import signature
from pathlib import Path
from typing import cast

from argparse_formatter import FlexiFormatter

from cheeto import __version__
from cheeto.sheet import SheetName

from .path import twiddles, user_data_path


DATA_PATH_ENV_VAR = "CHEETO_DATA_PATH"


def unpack_args(f):
    """Decorator for turning argparse Namespace into expected args (as kwargs).

    This decorator turns a function which expects to receive certain named arguments
    into one which expects to receive an argparse Namespace object (i.e. a set of parsed
    arguments); the decorator inspects the wrapped function's signature, and using that
    information it unpacks the Namespace, discarding names which don't occur in the
    wrapped function's signature, and passing it the rest as kwargs.

    It also:

      * Looks for an argument called 'args' and, if found, passes the entire Namespace
        object to that (unless there was already an item named 'args' in the Namespace,
        in which case that value is used).

      * Passes through any other kwargs it receives; if there are any name clashes
        between these explicitly passed kwargs and the contents of the Namespace (or the
        name 'args'), the explicitly passed kwarg version wins.

    This is particularly useful when writing 'command' functions (i.e. ones to be called
    directly after arg-parsing), as it allows us to just pass them the whole Namespace
    object without explicitly unpacking the desired items; instead, we just leave that
    to the command function's signature, effectively.
    """

    # Inspect the wrapped functions signature so that we only pass it elements of args
    # which it is interested in.
    parms = set(signature(f).parameters.keys())

    @wraps(f)
    def arg_unpacking_wrapper(args: argparse.Namespace, **kwargs):
        unpacked = {k: v for k, v in args.__dict__.items() if k in parms}
        if "args" in parms and "args" not in args:
            unpacked["args"] = args
        return f(**(unpacked | kwargs))

    return arg_unpacking_wrapper


class SubparserAction(argparse._SubParsersAction):
    def add_parser(self, name, *args, **kwargs):
        # Ensure that help and description are both set if either is.
        if "help" in kwargs and "description" not in kwargs:
            kwargs["description"] = kwargs["help"]
        elif "description" in kwargs and "help" not in kwargs:
            kwargs["help"] = kwargs["description"]
        subparser = super().add_parser(name, *args, **kwargs)
        # Ensure that aliases still result in the full name being used as dest.
        subparser.set_defaults(**{self.dest: name})
        return subparser

    def add_command_group_subparser(self, name, *args, **kwargs):
        return self.add_parser(name, *args, **kwargs).add_subparsers(
            dest="command",
            help="Command to execute; each has its own flags and --help",
            metavar="COMMAND",
            required=True,
        )


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        default_kwargs = {"formatter_class": FlexiFormatter}
        super().__init__(*args, **(default_kwargs | kwargs))
        self.add_version_argument()
        self.register("action", "parsers", SubparserAction)

    def add_boolean_switch_group(
        self,
        on_short: str,
        on_long: str,
        on_help: str,
        off_short: str,
        off_long: str,
        off_help: str,
        dest: str | None = None,
        default: bool | None = None,
    ):
        group = self.add_mutually_exclusive_group()
        group.add_argument(
            "--" + on_long,
            "-" + on_short,
            action="store_true",
            help=on_help + (" (default)" if default else ""),
            dest=dest if dest is not None else on_long,
            default=default,
        )
        group.add_argument(
            "--" + off_long,
            "-" + off_short,
            action="store_false",
            help=off_help + (" (default)" if default is False else ""),
            dest=dest if dest is not None else on_long,
            default=default,
        )

    def add_subparsers(self, *args, **kwargs) -> SubparserAction:
        sub = super().add_subparsers(*args, **kwargs)
        return cast(SubparserAction, sub)

    def add_debug_argument(self):
        self.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="Write debug output",
        )

    def add_version_argument(self):
        """Add a --version argument to a tool, reporting on library version.

        Here we use a specific argparse.Action subclass so that we can have this
        argument derail execution even if the parser otherwise defines some required
        arguments (which of course will be missing if the --version flag is given).  For
        more info see: https://stackoverflow.com/a/69789554
        """

        class _VersionAction(argparse.Action):
            def __init__(self, option_strings, dest, **kwargs):
                super().__init__(
                    option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs
                )

            def __call__(self, *args, **kwargs):
                sys.stdout.write(f"{__package__.split('.')[0]} version {__version__}\n")
                sys.exit(0)

        self.add_argument(
            "-V",
            "--version",
            action=_VersionAction,
            help="Show version information",
        )

    def add_data_path_arg(self):
        fallback_data_path = user_data_path("cheeto")
        default_data_path = Path(os.environ.get(DATA_PATH_ENV_VAR, fallback_data_path))
        self.add_argument(
            "-p",
            "--path",
            default=default_data_path,
            dest="data_path",
            help=(
                "Path to est-cli config; "
                f"default is contents of {DATA_PATH_ENV_VAR} env var if set "
                f"(now: {os.environ.get(DATA_PATH_ENV_VAR, 'unset')})"
                f"; otherwise {twiddles(fallback_data_path)}"
            ),
            metavar="PATH",
            type=Path,
        )

    def add_sheet_arg(self):
        self.add_argument(
            "sheet_name",
            help="Name of sheet as it appears in list of sheets",
            metavar="SHEET_NAME",
            type=SheetName,
        )


def positive_int(raw) -> int:
    value = int(raw)
    if value < 1:
        msg = f"{raw} is not a positive int"
        raise argparse.ArgumentTypeError(msg)
    return value
