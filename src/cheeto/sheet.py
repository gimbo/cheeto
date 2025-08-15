from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple, NewType, Self

from cheeto.utils.error import CheetoError
from cheeto.utils.pathlib import twiddles, walk


SheetName = NewType("SheetName", str)


class SheetError(CheetoError): ...


class SheetNameClashError(SheetError):
    """Found multiple sheets with same name (e.g. files `foo` and `foo.md`)."""


class SheetNotFoundError(SheetError): ...


class Sheet(NamedTuple):
    path: Path

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def name(self) -> SheetName:
        return self.normalize_sheet_name(self.path.stem)

    @staticmethod
    def normalize_sheet_name(name: str) -> SheetName:
        return SheetName(
            name[: -len(".cheatsheet")] if name.endswith(".cheatsheet") else name
        )

    @property
    def text(self) -> str:
        return self.path.expanduser().read_text()

    def __len__(self):
        return len(self.text)

    @property
    def first_non_empty_line(self) -> str:
        try:
            return next(line.strip() for line in self.text.splitlines())
        except StopIteration:
            return ""

    @property
    def title(self) -> str:
        first = self.first_non_empty_line
        if not first:
            return str(self.name)
        title = first[2:] if first.startswith("# ") else first
        return title if title else str(self.name)

    @property
    def probably_markdown(self) -> bool:
        return any(
            (
                self.path.suffix.lower() == ".md",
                self.first_non_empty_line.startswith("# "),
            )
        )

    @classmethod
    def find_cheatsheets_at(cls, path: Path) -> Iterator[Self]:
        for child in walk(path.expanduser()):
            if "cheatsheet" in child.name.split("."):
                yield cls(twiddles(child))
