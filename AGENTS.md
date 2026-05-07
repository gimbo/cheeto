# AGENTS.md

Compact guidance for agents working on `cheeto` (a terminal cheat-sheet utility). See `README.md` for user-facing docs.

## Toolchain

- Python **3.13** only (`.python-version` = 3.13.5, `requires-python = ">=3.13,<4"`).
- `uv` is the canonical tool — build backend is `uv_build`, deps locked in `uv.lock`. There is no `setup.py`/`setup.cfg`; do not add one.
- Load the `running-python` / `uv-package-manager` skills before invoking `python`, `uv`, `pytest`, etc.

## Layout

- `src/cheeto/` — package (src-layout). Entrypoint: `cheeto.scripts.cheeto:main` (wired in `[project.scripts]`).
- `src/cheeto/utils/markdown.py` — markdown renderers; new renderers are registered via the `cheeto.utils.markdown.renderers` entry point (see `pyproject.toml`), **not** by importing them directly.
- `tests/cheeto/` — pytest tests.
- `_cheeto` (repo root) — zsh completion script, **not** Python. Do not edit as code.
- `build/` — stale local build artefacts (checked in historically); ignore.

## Commands

Dev install:
```
uv sync            # creates .venv with dev group
uv run pre-commit install --install-hooks
```

Run the CLI:
```
uv run cheeto ...
```

Tests — note pytest has `--doctest-modules --cov` baked into `pyproject.toml`, so:
- `uv run pytest` runs the full suite **plus doctests in every module** plus coverage. Doctests in `src/` are live tests; breaking them fails CI.
- For a single test: `uv run pytest tests/cheeto/test_foo.py::test_bar --no-cov` (disable cov for speed/clarity on focused runs).
- The pre-commit `pytest` hook runs `.venv/bin/python -m pytest -x --no-cov -q > /dev/null` — output is suppressed; run pytest directly when debugging.

Lint / format / typecheck (all via pre-commit, or directly):
```
uv run ruff check --fix .
uv run ruff format .
uv run mypy src tests
uv run pre-commit run --all-files
```

Version bump (tags + edits `uv.lock`):
```
uv run bumpversion patch --verbose
```

## Gotchas

- `tests/cheeto/test_null.py` is a placeholder whose own docstring says to delete it once real tests exist. If you add real tests, remove it.
- Because `--doctest-modules` is enabled, any `>>>` examples added to docstrings in `src/cheeto/**` become tests. Keep that in mind when writing examples.
- `.envrc` sets `OCD_PROFILE=estima` and sources `.env`; direnv users only — not required to run the app.
- Cheat sheet discovery path resolution order (CLI `--path` → `CHEETO_DATA_PATH` → XDG `cheeto` dir) is enforced in code; preserve this order if touching path logic.
- `.opencode/opencode.jsonc` pins the OpenCode model/small_model for this repo.

## Conventions

- Follow the loaded `python-conventions` skill for style questions not covered by ruff.
- No emojis in code/docs unless explicitly requested (see repo-level author rules).
- Plan files under `.opencode/plans/` should be committed (per author's general rules) unless told otherwise.
