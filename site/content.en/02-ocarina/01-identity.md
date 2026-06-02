---
title: "02.01 — Ocarina's technical identity"
description: "Ocarina's technical identity through its pyproject.toml: name, version 1.1.9, Python 3.14+, minimal dependencies and quality toolchain."
weight: 1
date: 2026-05-20
series: ["ocarina"]
series_order: 1
tags: ["typing"]
---

# 02.01&nbsp;—&nbsp;Ocarina's technical identity

## `pyproject.toml`

```toml
[project]
name = "ocarina"
version = "1.1.9"
description = "Websites test framework for Igor"
requires-python = ">=3.14"
authors = [{ name="Igor Casanova", email="[REDACTED]" }]
license = "MIT"
license-files = ["LICEN[CS]E*"]
readme = "README.md"

dependencies = ["python-docx>=1.2.0"]
```

1. **`version = "1.1.9"`**: _stable 1.x_, not a pre-release.
2. **`requires-python = ">=3.14"`**: PEP 695 generic typing everywhere.
3. **`dependencies = ["python-docx>=1.2.0"]`**: **one** runtime dependency. The rest lives in `dev`.
4. **`license = "MIT"`**.
5. **`description = "Websites test framework for Igor"`**: not "for everyone," not "for humans," explicitly "for Igor." Lines up with [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md): "It's _my_ car."

## `dev` dependencies

```toml
[dependency-groups]
dev = [
    "ruff>=0.15.0",
    "mypy>=1.17.0",
    "mypy-extensions>=1.1.0",
    "typing-extensions>=4.14.0",
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "hypothesis>=6.151.0",
    "pytest-mypy-plugins>=3.1.0",
    "allure-pytest>=2.15.3",
    "allure-python-commons>=2.15.3",
    "pre-commit>=4.5.1",
    "syrupy>=5.1.0",
    "selenium>=4.40.0",
    "playwright>=1.60.0",
    "twine>=6.2.0",
    "build>=1.4.2",
    "prysk>=0.20.0",
]
```

| Tool                                      | Role in Ocarina                                                                                                                                                       |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ruff`                                    | Linter + formatter (replaces flake8 + isort + black). `select = ["ALL"]`.                                                                                             |
| `mypy` (+ extensions)                     | Type-checker. `strict = true` (see `mypy.ini`).                                                                                                                       |
| `pytest`                                  | Unit-test runner (the framework is itself tested).                                                                                                                    |
| `pytest-cov`                              | Test coverage (of the framework itself). Configured in `pyproject.toml#tool.coverage`.                                                                                |
| `hypothesis`                              | _Property-based testing (PBT)_ → `test_invariants_properties.py`.                                                                                                     |
| `pytest-mypy-plugins`                     | **Static** typing tests (checks expected _mypy_ errors and type-inference tests with `reveal_type`).                                                                  |
| `allure-pytest` / `allure-python-commons` | Allure report (deployed to GH Pages).                                                                                                                                 |
| `pre-commit`                              | Local git hooks (ruff-format).                                                                                                                                        |
| `syrupy`                                  | _Snapshot testing_ (output of `pretty_print_results`, `results_to_json`).                                                                                             |
| `selenium`                                | Present in `dev` because Ocarina **doesn't depend** on Selenium to work; it just ships a Selenium _adapter_ so the framework is immediately operational out of box.   |
| `playwright`                              | Same logic: a second shipped _adapter_ (since `1.1.3`). Ocarina now drives **both** Selenium and Playwright out of the box, behind the same ports.                    |
| `twine` / `build`                         | PyPI publishing.                                                                                                                                                      |
| `prysk`                                   | CLI tests in the _cram_ (`.t`) format. Successor to `cram`.                                                                                                           |

## `mypy.ini`

```ini
[mypy]
python_version = 3.14
strict = true

# * ... Allow missing annotations (type inference is cool)
disallow_incomplete_defs = false

# * ... Allow missing annotations (type inference is cool)
disallow_untyped_defs = false
```

- **`strict = true`**: enables `--warn-redundant-casts`, `--warn-unused-ignores`, `--no-implicit-optional`, `--check-untyped-defs`, etc.
- Two exceptions: `disallow_incomplete_defs` and `disallow_untyped_defs` are off. _mypy_'s **type inference** is good enough when explicit annotations don't add value. Annotations live where they actually **matter**.

## `pyproject.toml#tool.ruff`

```toml
[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "ANN002", "ANN003", "ANN201",
    "TRY003",
    "C901",
    "D203",    # conflict with D211
    "D213",    # conflict with D212
    "COM812",  # conflict with the ruff formatter (auto-fix)
]

[tool.ruff]
exclude = ["**/.venv/**", "**/bin/**", "**/__init__.py", "**/__bypass_linter__"]
```

- **`select = ["ALL"]`**: every _ruff_ rule on (~800).
- **Short ignore list**: six rules, each one justified.
- **`B008` must NEVER be ignored** ("_`# "B008",  # * ... NEVER ignore this rule without knowing very well what you are doing: https://docs.astral.sh/ruff/rules/function-call-in-default-argument/`_"). Note left so the past mistake doesn't repeat.
- **`**/**bypass_linter**`\*\*: directory convention for explicitly un-linted code (handy for internal experimental modules).

## `pyproject.toml#tool.pytest.ini_options`

```toml
testpaths = ["tests"]
python_files = ["test_*.py"]
norecursedirs = [".*", "__pycache__"]
log_cli = true
log_cli_level = "DEBUG"
log_cli_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
addopts = """
--cov=src
--cov-branch
--cov-report=term-missing
--cov-report=html
--cov-report=xml:coverage.xml
"""
```

| Setting                      | Effect                                                                             |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| `log_cli = true`             | All test logs surface in the CLI (useful for scenarios that go through `ILogger`). |
| `--cov=src` + `--cov-branch` | Branch coverage, not just line coverage.                                           |
| `--cov-report=html` + `xml`  | Three outputs: terminal, local HTML, XML for CI ingestion.                         |

## `pyproject.toml#tool.coverage`

Full detail at [`../04-internal-tests/07-coverage-policy.md`](../04-internal-tests/07-coverage-policy.md). Short version: anything that's pure _shape_ (custom_types, ports, errors), anything that needs a real browser (Selenium adapters), and anything covered by cram tests (cli/store, cli/builder) is explicitly omitted. Otherwise the metrics **lie**.

## `Makefile`

| Recipe                             | Effect                                                                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `make install`                     | Creates `.venv` if absent, `pip install -e . --group dev`, `pre-commit install`. Cross-OS (Windows / other).              |
| `make install-on-ci`               | CI variant: `pip install -r requirements-dev.txt` then `pip install -e . --no-deps`.                                      |
| `make test`                        | `make cram-test` then `pytest --alluredir=allure-results -vv --hypothesis-show-statistics` then copies `categories.json`. |
| `make cram-test`                   | `prysk tests/cram/` (on Windows: no-op).                                                                                  |
| `make check-coding-style`          | `mypy + ruff`                                                                                                             |
| `make mypy-check`                  | `mypy src/ tests/`                                                                                                        |
| `make ruff-check`                  | `ruff check .`                                                                                                            |
| `make ruff-format`                 | `ruff format .`                                                                                                           |
| `make generate-allure`             | `allure generate allure-results -o allure-report`                                                                         |
| `make serve-allure`                | Opens the Allure report in a browser.                                                                                     |
| `make serve-htmlcov`               | Same for `htmlcov/`.                                                                                                      |
| `make test-ui`                     | `make test` + `make generate-allure` + `make serve-htmlcov` + `make serve-allure`                                         |
| `make update-snapshots`            | `pytest --snapshot-update`                                                                                                |
| `make clean` / `make clean-allure` | Cross-OS cleanup.                                                                                                         |

## `categories.json` (Allure taxonomy)

```json
[
  {
    "name": "Test defects",
    "matchedStatuses": ["broken"],
    "messageRegex": ".*"
  },
  {
    "name": "Invariant violations",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*InvariantViolationError.*"
  },
  {
    "name": "Assertion errors",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*AssertionError.*"
  },
  { "name": "Skipped", "matchedStatuses": ["skipped"], "messageRegex": ".*" }
]
```

Four categories. _Invariant violations_, for instance, catches failures that come from `validate(...).execute().raise_if_invalid()`.

## `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.11
    hooks:
      - id: ruff-format
```

Minimal: just `ruff-format` on pre-commit. The rest (`ruff check`, `mypy`) is CI-only. Local friction stays low&nbsp;—&nbsp;don't get in the developer's way.

## URLs

```toml
[project.urls]
Documentation = "https://mojo-molotov.github.io/ocarina-holy-book"
Homepage      = "https://github.com/mojo-molotov/ocarina"
Issues        = "https://github.com/mojo-molotov/ocarina/issues"
```

The `Documentation` URL points to the **Holy Book**. See [`../09-holy-book/`](../09-holy-book/README.md)

## Build backend

```toml
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"
```

`hatchling`: modern (PEP 517/518), lightweight, zero _ad hoc_ config.
