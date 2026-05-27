---
title: "04.02 — Cram tests (prysk)"
description: "CLI tests in cram format: a .t file contains shell commands and their expected output. Tool: prysk (modern rewrite of the original cram)."
weight: 2
date: 2026-05-20
series: ["internal-tests"]
series_order: 2
---

# 04.02&nbsp;—&nbsp;Cram tests (`prysk`)

> CLI tests in _cram_ format: a `.t` file contains shell commands and their expected output. Tool: `prysk` (modern rewrite of the original `cram`).

## `.t` file

```
Valid args produce a deterministic parsed config

  $ touch driver
  $ "$PYTHON" "$TESTDIR/_demo_cli.py" --browser firefox --driver-path driver --workers 3 --wait-timeout 20 --logger terminal
  browser=firefox
  driver_path=driver
  headless=True
  workers=3
  wait_timeout=20
  logger=terminal
  only=()
  exclude=()
```

- First line: title (comment for the human).
- Blank line.
- Lines starting with ` $`: shell command run.
- Following lines (indent 2): expected output.

Actual output differs → test fails.

## `_demo_cli.py`

```python
# tests/cram/_demo_cli.py
"""Tiny CLI that pushes a SeleniumCliStoreSingleton and prints its content."""

from ocarina.opinionated.cli.selenium.cli_store_singleton import (
    SeleniumCliStoreSingleton as CliStoreSingleton,
)
from ocarina.opinionated.cli.selenium.create_cli_store import (
    create_selenium_auto_cli_store,
)

if __name__ == "__main__":
    CliStoreSingleton().push(create_selenium_auto_cli_store())
    for key in ("browser", "driver_path", "headless", "workers", "wait_timeout", "logger", "only", "exclude"):
        print(f"{key}={CliStoreSingleton().get(key)}")
```

→ Prints the store contents _deterministically_. Cram diffs the output line by line.

## `.t` files

| File                         | Verifies                                                          |
| ---------------------------- | ----------------------------------------------------------------- |
| `cli_happy_path.t`           | A valid combination produces the right output                     |
| `cli_defaults.t`             | Defaults are parsed correctly                                     |
| `cli_help.t`                 | `--help` lists the _n_ flags                                      |
| `cli_invalid_browser.t`      | `--browser=banana` raises cleanly                                 |
| `cli_invalid_wait_timeout.t` | `--wait-timeout=0` raises (`is_not_zero`)                         |
| `cli_missing_driver_path.t`  | `--browser=chrome` without `--driver-path` raises                 |
| `cli_not_headless_flag.t`    | `--not-headless` inverts the default (stored as `headless=False`) |
| `cli_only_flag.t`            | `--only id1 id2` parses a list                                    |
| `cli_exclude_flag.t`         | `--exclude id1 id2` parses a list                                 |
| `cli_only_exclude_mutex.t`   | `--only` and `--exclude` together raises                          |

## `cli_help.t`

```
CLI --help lists every declared flag

Pipe through grep to stay resilient to unrelated wording changes in argparse's
help output. Sorted unique output → alphabetical by first-differing character.

  $ "$PYTHON" "$TESTDIR/_demo_cli.py" --help 2>&1 | grep -o -- '--\(driver-path\|profile-path\|browser\|not-headless\|workers\|logger\|wait-timeout\|dont-force-delete-tmp-dirs\|only\|exclude\)' | sort -u
  --browser
  --dont-force-delete-tmp-dirs
  --driver-path
  --exclude
  --logger
  --not-headless
  --only
  --profile-path
  --wait-timeout
  --workers
```

We don't test `--help`'s **full output** (it shifts with argparse versions), just that the listed flags appear at **minimum**. `grep` each flag, then `sort -u`. Missing flag → output differs, test fails.

We test what matters, nothing more.

## `Makefile`

```makefile
.PHONY: cram-test
cram-test:
ifeq ($(OS),Windows_NT)
	@echo "N A P O L E O N  D I S A P P R O V E S  W I N D O W S"
else
	@echo "Running cram tests..."
	PYTHON="$(CURDIR)/$(VENV_PYTHON)" "$(CURDIR)/$(VENV_BIN)/prysk" tests/cram/
endif
```

1. **Skip on Windows**. Prysk doesn't have the same shell support on Windows; Napoleon told the author to skip cleanly instead of fighting it.
2. **`PYTHON` injected**: Prysk substitutes `$PYTHON` in `.t` files with the venv Python's path.
3. **`prysk tests/cram/`**: runs every `.t` in the folder.

## Why cram rather than pytest for the CLI

| Cram                                         | pytest                                                         |
| -------------------------------------------- | -------------------------------------------------------------- |
| Test = shell command + expected output (1-1) | Test = Python code calling, capturing stdout/stderr, asserting |
| Readable by non-Python folks                 | Requires understanding Python                                  |
| Naturally captures stderr too                | `capsys` to configure                                          |
| No mocks to set up                           | Often mocks                                                    |
| Readable failure (line-by-line diff)         | More noise                                                     |

The CLI is a _user interface_, not Python code. Cram is the natural tool&nbsp;—&nbsp;the most appropriate "system test" here.

## `make test`

```makefile
.PHONY: test
test: cram-test
	@echo "Running tests..."
	-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
	$(PY_CMD) -c "import shutil; shutil.copy('categories.json', '$(ALLURE_RESULTS)/categories.json')"
```

→ `make test` chains:

1. `cram-test` (the `.t`s).
2. `pytest` with Allure output + `--hypothesis-show-statistics`.
3. Copy of `categories.json` to `allure-results/`.

If `cram-test` fails, `pytest` doesn't run (Makefile target dependency). The `-` before `pytest` lets execution continue even if pytest fails (so we still get the Allure report).
