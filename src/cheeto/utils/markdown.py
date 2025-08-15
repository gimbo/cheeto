from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod
from importlib.metadata import entry_points
from pathlib import Path

from rich import get_console
from rich.console import RenderableType, Console, ConsoleOptions, RenderResult
from rich.markdown import Markdown, Heading
from rich.text import Text

from .pathlib import is_executable, is_executable_in_path


logger = logging.getLogger(__name__)


class MarkdownRenderer(ABC):
    @abstractmethod
    def __call__(self, src: str) -> RenderableType: ...

    def __bool__(self) -> bool:
        """Is the renderer available?"""
        # Subclasses may override this in order to check.
        return True

    @classmethod
    def renderers(cls) -> dict[str, MarkdownRenderer]:
        """Compute available renderers/names from entry points."""
        renderers = {
            ep.name: ep.load()()
            for ep in entry_points(group="cheeto.utils.markdown.renderers")
        }
        return {name: renderer for name, renderer in renderers.items() if renderer}


class NullRenderer(MarkdownRenderer):
    """Render markdown source as plain text."""

    def __call__(self, src: str) -> RenderableType:
        return src


class MyMarkdown(Markdown):
    """Custom rich.Markdown

    I didn't love how rich.markdown rendered headers as centred by default, but
    it turns out [1] it's easy to override.

    [1] https://github.com/Textualize/rich/issues/2137
    """

    class _MyHeading(Heading):
        """Custom rich.Heading for left-aligned headers."""

        def __rich_console__(
            self,
            console: Console,
            options: ConsoleOptions,
        ) -> RenderResult:
            depth = int(self.tag.lstrip("h"))
            if depth == 2:
                yield Text("")
            yield Text.assemble("#" * depth, " ", self.text, style="green4")

    elements = Markdown.elements | {"heading_open": _MyHeading}


class RichRenderer(MarkdownRenderer):
    """Render markdown using rich.Markdown; this is the default."""

    def __call__(self, src: str) -> RenderableType:
        return MyMarkdown(src)


class ExternalMarkdownRenderer(MarkdownRenderer, ABC):
    def __init__(self, executable: Path | str):
        self._executable = executable

    def __bool__(self) -> bool:
        return (
            is_executable_in_path(self._executable)
            if isinstance(self._executable, str)
            else is_executable(self._executable)
        )


class MdcatRenderer(ExternalMarkdownRenderer):
    """Render markdown using the mdcat tool if available."""

    def __init__(self, executable: Path | None = None):
        super().__init__(executable if executable is not None else "mdcat")

    def __call__(self, src: str) -> RenderableType:
        cmd = ["mdcat", "-"]
        logger.debug(cmd)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            encoding="utf-8",
            input=src,
        )
        return proc.stdout


class GlowRenderer(ExternalMarkdownRenderer):
    """Render markdown using the glow tool if available."""

    MODE = "dark"

    def __init__(self, executable: Path | None = None):
        super().__init__(executable if executable is not None else "glow")

    def __call__(self, src: str) -> RenderableType:
        cmd = ["glow", "-s", self.MODE, "-w", str(get_console().width)]
        logger.debug(cmd)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            encoding="utf-8",
            input=src,
        )
        return proc.stdout


class GlowLightRenderer(GlowRenderer):
    """Render markdown using glow tool if available (light mode)"""

    MODE = "light"
