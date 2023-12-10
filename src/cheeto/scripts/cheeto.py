"""Some script."""

import json
import logging
import sys
from contextlib import suppress
from enum import Enum
from pathlib import Path

import humanize
from rich import box, pretty, print, reconfigure, traceback
from rich.logging import RichHandler
from rich.table import Table

from cheeto.sheet import SheetName, SheetNameClashError, SheetNotFoundError
from cheeto.sheets import Sheets
from cheeto.utils.argparse import ArgumentParser, unpack_args
from cheeto.utils.markdown import MarkdownRenderer


logger = logging.getLogger(__name__)
pretty.install()
traceback.install(show_locals=True)


def main():
    reconfigure(markup=False)
    args = parse_args()
    logging.basicConfig(
        level="DEBUG" if args.debug else "INFO",
        format="%(message)s",
        datefmt="%Y-%m-%d%H:%M:%S+%z",
        handlers=[RichHandler()],
    )
    logger.debug("Args: %s", args)
    args.func(args)


class OutputFormat(Enum):
    """Output format for the 'list sheets' command."""

    PLAIN = "plain"
    TABLE = "table"
    JSON = "json"


@unpack_args
def cmd_list_sheets(data_path: Path, sheets: Sheets, output_format: OutputFormat):
    if output_format == OutputFormat.TABLE:
        print(tabulate_sheets(data_path, sheets))
    elif output_format == OutputFormat.JSON:
        print(jsonify_sheets(sheets))
    else:
        print(list_sheet_names(sheets))


def list_sheet_names(sheets: Sheets) -> str:
    return "\n".join(str(sheet_name) for sheet_name in sheets)


def tabulate_sheets(data_path: Path, sheets: Sheets):
    table = Table(box=box.MINIMAL, title=str(data_path))
    table.add_column("Name")
    table.add_column("Filename")
    table.add_column("Title")
    table.add_column("Size")
    table.add_column("MD?")
    for sheet_name, sheet in sheets.items():
        table.add_row(
            sheet_name,
            sheet.filename if sheet.filename != sheet.name else "",
            sheet.title,
            humanize.naturalsize(len(sheet.text), binary=True),
            "✓" if sheet.probably_markdown else "",
        )
    return table


def jsonify_sheets(sheets: Sheets) -> str:
    return json.dumps(
        [
            {
                "name": sheet.name,
                "path": str(sheet.path),
                "title": sheet.title,
                "size": len(sheet),
                "markdown": sheet.probably_markdown,
            }
            for sheet in sheets.values()
        ],
        indent=2,
    )


@unpack_args
def cmd_show_sheet(
    data_path: Path,
    sheet_name: SheetName,
    markdown_renderer: MarkdownRenderer,
):
    try:
        sheet = Sheets.named_sheet_at(sheet_name, data_path)
    except SheetNotFoundError:
        print(f"Can't find sheet '{sheet_name}' at path [{data_path}]")
        return
    if not sheet.probably_markdown:
        print(sheet.text)
        return
    rendered = markdown_renderer(sheet.text)
    if isinstance(rendered, str):
        sys.stdout.write(rendered)
    else:
        print(rendered)


def parse_args(args_raw: tuple[str, ...] = tuple(sys.argv[1:])):
    parser = ArgumentParser(
        description=__doc__,
    )
    parser.add_debug_argument()
    parser.add_data_path_arg()

    cmd_parsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
        required=True,
        help="Command to execute; each has its own args and --help",
    )
    cmd_list_sheets_parser = cmd_parsers.add_parser(
        "list-sheets",
        aliases=["ls"],
        description="List available sheets",
    )
    format_group = cmd_list_sheets_parser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--plain",
        "-P",
        action="store_const",
        dest="output_format",
        const=OutputFormat.PLAIN,
        default=OutputFormat.PLAIN,
        help=(
            "Plain format: just list the discovered cheatsheet names, one per line; "
            "this is the default output format"
        ),
    )
    format_group.add_argument(
        "--table",
        "-t",
        action="store_const",
        dest="output_format",
        const=OutputFormat.TABLE,
        help="Show a table of more detailed discovered cheatsheet information",
    )
    format_group.add_argument(
        "--json",
        "-j",
        action="store_const",
        dest="output_format",
        const=OutputFormat.JSON,
        help="Write out JSON describing the discovered cheatsheets",
    )
    cmd_list_sheets_parser.set_defaults(func=cmd_list_sheets)

    cmd_show_sheet_parser = cmd_parsers.add_parser(
        "show-sheet",
        aliases=["s", "show"],
        description="Show specified sheet",
    )
    available_renderers = MarkdownRenderer.renderers()
    renderer_helps = [
        f"* {name}: {renderer.__doc__}"
        for name, renderer in available_renderers.items()
    ]
    cmd_show_sheet_parser.add_argument(
        "--markdown",
        "-m",
        choices=list(available_renderers),
        default="rich",
        dest="markdown_renderer_class",
        help=(
            "Renderer to use for displaying markdown sheets; choices:\n\n"
            + "\n".join(renderer_helps)
        ),
    )
    cmd_show_sheet_parser.add_sheet_arg()
    cmd_show_sheet_parser.set_defaults(func=cmd_show_sheet)

    args = parser.parse_args(args_raw)
    # If a markdown renderer was specified, use it.
    with suppress(AttributeError):
        args.markdown_renderer = dict(available_renderers)[args.markdown_renderer_class]

    try:
        args.sheets = Sheets.at(args.data_path)
    except SheetNameClashError as ex:
        name, first, second = ex.args
        sys.stderr.write(f"Sheet name clash:\n  {name}\n  {first}\n  {second}\n")
        sys.exit(1)

    return args
