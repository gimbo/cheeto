# cheeto - a (terminal) cheat sheet utility

This is `cheeto`, a simple cheat sheet utility (written in python) which looks in some known folder for textual cheat sheets and writes their contents to the terminal, rendering markdown if found.



## Installation

[uv](https://docs.astral.sh/uv/) rules the roost! Either:

```
uv tool install git+https://github.com/gimbo/cheeto
```

or to just run it once:

```
uvx --from git+https://github.com/gimbo/cheeto cheeto
```

### No `uv`?

[pipx](https://github.com/pypa/pipx) is recommended:

```shell
pipx install <path to this folder>
```

should work; check it with:

```shell
$ cheeto --version
cheeto version 1.0.0
```

### Installation of zsh completions

To install zsh completions for the `cheeto` command, install this repo as a zsh plugin using your plugin manager of choice.  Note that this **does not** install the `cheeto` command itself: just its completions.

## Usage

### Cheat sheet location

`cheeto` looks for cheat sheets (which are just files whose name contains the text `cheatsheet`) in a single folder and its children, recursively; that root is specified as follows:

* By the `--path`/`-p` command line argument if set.
* Otherwise, by the `CHEETO_DATA_PATH` env var if set (here, `~` will be expanded).
* Otherwise, it falls back on the XDG base directory specification, looking for a folder called `cheeto` in `XDG_DATA_HOME`.

If in doubt, `cheeto --help` will show you the current status, e.g.:

```shell
$ cheeto --help

  -p PATH, --path PATH  Path to est-cli config; default is contents of
                        CHEETO_DATA_PATH env var if set (now:
                        ~/.config/cheeto/sheets); otherwise
                        ~/Library/Application Support/cheeto
```

(in this example `~/Library/Application` is the value of `XDG_DATA_HOME` — the default on macOS).



### List discovered sheets:

```shell
cheeto ls [--plain | --table | --json]
```

* `--plain` — just the sheet names (see below), one per line.
* `--table` — a table containing more detailed information on each sheet.
* `--json` — sheet detail (like `--table`) but in JSON format.

N.b.: in general the **name** of each cheat sheet is its filename without suffix and without `.cheatsheet` if that's the last text before the suffix; e.g. a cheatsheet in the file `foo.cheatsheet.md` will have name `foo`.  However, if two cheat sheets with the same name are discovered in different paths, each one's shortest distinct path prefix (with respect to the others of the same name) is added to the name; e.g. if we have `foo/bar/baz.cheatsheet.md` and `foo/gar/baz.cheatsheet.md` their names will be `bar/baz` and `gar/baz` respectively.  If names still clash even after such a transformation (e.g. if you have `foo/bar/baz.cheetsheet.md` and `foo/bar/baz.cheatsheet`) then `cheeto` will complain and exit.


### Show specified sheet:

```shell
cheeto show <sheet_name>
```

This loads the sheet (specified using its name as shown by `cheeto ls`) and writes its contents to the terminal.

#### Markdown sheets

`cheeto` will try to determine if the sheet is in markdown format; it uses a simple heuristic: it's considered markdown if the sheet's filename ends in `.md` or if the sheet's first line looks like a markdown level-1 header in `#` format — e.g. `# <blah`.

Then, the markdown is rendered using one of a number of available renderers, controlled using the `--markdown-renderer` / `-m` option; these may be extended (see below) but by default the options are:

* `rich` — (the default) use the [`rich`](https://rich.readthedocs.io/en/stable) python package to render the markdown.
* `null` — render the markdown as plain text.
* `mdcat` — use the [`mdcat`](https://github.com/swsnr/mdcat) tool.
* `glow` — use the [`glow`](https://github.com/swsnr/mdcat) tool (in dark mode).
* `glowl` — use the [`glow`](https://github.com/swsnr/mdcat) tool (in light mode).

The `mdcat` and `glow`/`glowl` options will only appear if those tools appear to be in the `$PATH`.

This list may be extended without modifying this package's code, via python's entry points machinery: implement a subclass of the ABC `cheeto.utils.markdown.MarkdownRenderer` and register it with the `cheeto.utils.markdown.renderers` entry point.



## Background / inspiration

This is inspired by the [0b10/cheatsheet](https://github.com/0b10/cheatsheet) zsh plugin.  I tried that for a while but realised it didn't quite fit my needs:

* I only needed a tool to list and display cheatsheets  — not one to _manage_ (add, edit, etc.)
* I want to write my cheatsheets in markdown, and then I want them rendered in the terminal using e.g. [mdcat](https://github.com/swsnr/mdcat)...
  - ... and while I can pipe the output of that cheatsheet plguin to mdcat, the plugin strips all lines beginning with `#` as comments — so no markdown headings!
* I want my cheatsheets to be spread across multiple folders, and identified by a particular filename pattern.
* Finally, I wanted the "show cheatsheet" command to have tab completion listing the sheets.



## Installation for dev

* Create a venv
* `pip install -U pip setuptools`
* `pip install -e ".[dev]"`
* `pre-commit install --install-hooks`

### Bumping versions

Use bump2version; e.g.:

```
bumpversion patch --verbose
```
