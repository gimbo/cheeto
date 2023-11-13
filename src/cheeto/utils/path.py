import os
from functools import wraps
from pathlib import Path
from typing import Protocol

import platformdirs


def twiddles(path: Path):
    """Inverse of path.expanduser() for current user: replace home path with ~

    Trivially, there is no change if the path starts with ~

    >>> from pathlib import PosixPath
    >>> twiddles(PosixPath('~'))
    PosixPath('~')
    >>> twiddles(PosixPath('~/config'))
    PosixPath('~/config')

    There is also no change if the path is not relative to ~

    >>> twiddles(Path('/tmp/foo'))
    PosixPath('/tmp/foo')
    >>> twiddles(Path('/tmp/foo'))
    PosixPath('/tmp/foo')

    But where the path is relative to (expanded) home directory, it is returned  with
    the ~ symbol back in place.

    >>> home = str(PosixPath('~').expanduser().resolve())
    >>> "~" in home
    False
    >>> twiddles(Path(f'{home}'))
    PosixPath('~')
    >>> twiddles(Path(f'{home}/'))
    PosixPath('~')
    >>> twiddles(Path(f'{home}/config'))
    PosixPath('~/config')

    """
    if path.is_relative_to(Path("~").expanduser()):
        return Path("~") / path.relative_to(Path("~").expanduser())
    return path


class PlatformDirsUserFn(Protocol):
    """Loose specification of the type of a platformdirs.user_*_path() function."""

    def __call__(self, appname: str | None = None, *args, **kwargs) -> Path:
        ...


class UserPathFn(Protocol):
    """The type of the wrapped functions we create below."""

    def __call__(self, appname: str | None = None) -> Path:
        ...


# Functions which wrap platformdirs.*_path() but which honour XDG_* env vars if set.
#
# XDG env var meanings are defined here:
# https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
def xdg_platformdirs(fn: PlatformDirsUserFn, env_var: str) -> UserPathFn:
    @wraps(fn)
    def inner(appname: str | None = None) -> Path:
        try:
            xdg_dir = os.environ[env_var]
        except KeyError:
            return fn(appname)
        return twiddles(Path(xdg_dir) / ("" if appname is None else appname))

    return inner


user_data_path = xdg_platformdirs(platformdirs.user_data_path, "XDG_DATA_HOME")
user_config_path = xdg_platformdirs(platformdirs.user_config_path, "XDG_CONFIG_HOME")
user_cache_path = xdg_platformdirs(platformdirs.user_cache_path, "XDG_CACHE_HOME")
user_state_path = xdg_platformdirs(platformdirs.user_state_path, "XDG_STATE_HOME")
user_runtime_path = xdg_platformdirs(platformdirs.user_runtime_path, "XDG_RUNTIME_DIR")
