from collections.abc import Iterator
from itertools import groupby
from operator import attrgetter
from pathlib import Path
from typing import Mapping, Self

from cheeto.utils.pathlib import common_path_prefix

from .sheet import Sheet, SheetName, SheetNameClashError, SheetNotFoundError


class Sheets(Mapping):
    def __init__(self, sheets: dict[SheetName, Sheet], *args, **kwargs):
        self._sheets = sheets
        super().__init__(*args, **kwargs)

    @classmethod
    def of(cls, sheets: Iterator[Sheet]) -> Self:
        # Group discovered sheets by name, so we can detect and deal with duplicates.
        groups = [
            list(group)
            for _, group in groupby(
                sorted(sheets, key=attrgetter("name")), key=attrgetter("name")
            )
        ]
        # Find instances of the same sheet name, and if there are any, remove their
        # common prefix and use those names (normalized).
        normalized = {}
        for group in groups:
            if len(group) == 1:
                normalized[group[0].name] = group[0]
            else:
                common_prefix = common_path_prefix(
                    [sheet.path.parent for sheet in group]
                )
                for sheet in group:
                    parent = sheet.path.parent.relative_to(common_prefix)
                    name = Sheet.normalize_sheet_name(
                        str((parent / sheet.filename).with_suffix(""))
                    )
                    if name in normalized:
                        raise SheetNameClashError(
                            name,
                            normalized[name].path,
                            sheet.path,
                        )
                    normalized[name] = sheet

        return cls(dict(sorted(normalized.items())))

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
