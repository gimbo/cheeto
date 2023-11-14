from collections.abc import Iterator
from operator import attrgetter
from pathlib import Path
from typing import Mapping, Self

from .sheet import Sheet, SheetName, SheetNameClashError, SheetNotFoundError


class Sheets(Mapping):
    def __init__(self, sheets: dict[SheetName, Sheet], *args, **kwargs):
        self._sheets = sheets
        super().__init__(*args, **kwargs)

    @classmethod
    def of(cls, sheets: Iterator[Sheet]) -> Self:
        _sheets: dict[SheetName, Sheet] = {}
        for sheet in sorted(sheets, key=attrgetter("name")):
            if sheet.name in _sheets:
                raise SheetNameClashError(
                    sheet.name,
                    _sheets[sheet.name].path,
                    sheet.path,
                )
            _sheets[sheet.name] = sheet
        return cls(_sheets)

    @classmethod
    def at(cls, sheets_path: Path) -> Self:
        return cls.of(Sheet.find_cheatsheets_at(sheets_path))

    @classmethod
    def named_sheet_at(cls, sheet_name: SheetName, sheets_path: Path) -> Sheet:
        try:
            return Sheets.at(sheets_path)[sheet_name]
        except KeyError:
            raise SheetNotFoundError((sheet_name, sheets_path))

    def __getitem__(self, key):
        return self._sheets.__getitem__(key)

    def __iter__(self):
        return self._sheets.__iter__()

    def __len__(self):
        return self._sheets.__len__()
