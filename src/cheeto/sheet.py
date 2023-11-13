from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple, NewType, Self

from cheeto.utils.error import CheetoError
from cheeto.utils.path import twiddles


SheetName = NewType("SheetName", str)


class SheetError(CheetoError):
    ...


class SheetNameClashError(SheetError):
    """Found multiple sheets with same name (e.g. files `foo` and `foo.md`)."""


class SheetNotFoundError(SheetError):
    ...


class Sheet(NamedTuple):
    path: Path

    @classmethod
    def named_sheet_at(cls, sheet_name: SheetName, sheets_path: Path) -> Self:
        try:
            return Sheets.at(sheets_path)[sheet_name]
        except KeyError:
            raise SheetNotFoundError((sheet_name, sheets_path))

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def name(self) -> SheetName:
        return SheetName(self.path.stem)

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


class Sheets(Mapping):
    def __init__(self, sheets: dict[SheetName, Sheet], *args, **kwargs):
        self._sheets = sheets
        super().__init__(*args, **kwargs)

    @classmethod
    def at(cls, sheets_path: Path) -> Self:
        sheets: dict[SheetName, Sheet] = {}
        for path in sorted(sheets_path.expanduser().iterdir()):
            sheet = Sheet(twiddles(path))
            if sheet.name in sheets:
                raise SheetNameClashError(sheets[sheet.name].path, twiddles(path))
            sheets[sheet.name] = sheet
        return cls(sheets)

    def __getitem__(self, key):
        return self._sheets.__getitem__(key)

    def __iter__(self):
        return self._sheets.__iter__()

    def __len__(self):
        return self._sheets.__len__()
