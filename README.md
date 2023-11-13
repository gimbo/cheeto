# cheeto - a (terminal) cheat sheet utility

This is `cheeto`, a simple cheat sheet utility (written in python) which looks in some known folder for textual cheat sheets and writes their contents to the terminal, rendering markdown if found.



## Installation

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

`cheeto` looks for cheat sheets in a single (flat) folder; that is specified as follows:

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

N.b.: the **name** of each cheat sheet is its filename without suffix; e.g. a cheatsheet in the file `foo.md` will have name `foo`.  It's an error to have two sheets with the same name (e.g. `foo.md` and `foo.txt` or indeed just `foo`).


### Show specified sheet:

```shell
cheeto show <sheet_name>
```

This loads the sheet (specified using its _name_ - so no file suffix) and writes its contents to the terminal; `cheeto` will render the sheet using `mdcat` if it thinks it's in markdown format (either because its filename ends in `.md` or its first line looks like `# <blah` formatted a markdown level-1 header)


## Background / inspiration

This is inspired by the [0b10/cheatsheet](https://github.com/0b10/cheatsheet) zsh plugin.  I tried that for a while but realised it didn't quite fit my needs:

* I only needed a tool to list and display cheatsheets  — not one to _manage_ (add, edit, etc.)
* I want to write my cheatsheets in markdown, and then I want them rendered in the terminal using e.g. [mdcat](https://github.com/swsnr/mdcat)...
  - ... and while I can pipe the output of that cheatsheet plguin to mdcat, the plugin strips all lines beginning with `#` as comments — so no markdown headings!
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
