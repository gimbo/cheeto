import tomllib
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path


class ProjectInfo:
    """Obtain info about the current project & packages, for use by invoke tasks."""

    def __init__(self):
        self._python_version = Path(".python-version").read_text().strip()
        self._pyproject = tomllib.loads(Path("pyproject.toml").read_text())
        self._uv_lock = tomllib.loads(Path("uv.lock").read_text())

    @property
    def python_version(self) -> str:
        return self._python_version

    @property
    def project_name(self) -> str:
        return self._pyproject["project"]["name"]

    @property
    def project_package_version(self) -> str:
        return version(self.project_name)

    @property
    def prefect_version(self):
        return self.pinned_version_of("prefect")

    @property
    def uv_version(self):
        return self.pinned_version_of("uv")

    @lru_cache
    def pinned_version_of(self, name: str) -> str:
        """Get pinned version of some package from `uv.lock`"""
        packages = self._uv_lock["package"]
        try:
            package = next(package for package in packages if package["name"] == name)
        except StopIteration:
            raise KeyError(name)
        return package["version"]
