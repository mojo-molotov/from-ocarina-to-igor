---
title: "02.01 — Identité technique d'Ocarina"
description: "L'identité technique d'Ocarina via son pyproject.toml : nom, version 1.1.8, Python 3.14+, dépendances minimales et toolchain de qualité."
weight: 1
date: 2026-05-20
series: ["ocarina"]
series_order: 1
tags: ["typage"]
---

# 02.01&nbsp;—&nbsp;Identité technique d'Ocarina

## `pyproject.toml`

```toml
[project]
name = "ocarina"
version = "1.1.8"
description = "Websites test framework for Igor"
requires-python = ">=3.14"
authors = [{ name="Igor Casanova", email="[REDACTED]" }]
license = "MIT"
license-files = ["LICEN[CS]E*"]
readme = "README.md"

dependencies = ["python-docx>=1.2.0"]
```

1. **`version = "1.1.8"`**&nbsp;: le projet est en _stable 1.x_, pas en pré-version.
2. **`requires-python = ">=3.14"`**&nbsp;: le typage générique PEP 695 est utilisé partout.
3. **`dependencies = ["python-docx>=1.2.0"]`**&nbsp;: **une seule** dépendance d'exécution. Tout le reste est dans `dev`.
4. **`license = "MIT"`**.
5. **`description = "Websites test framework for Igor"`**&nbsp;: pas «&nbsp;_for everyone_&nbsp;», pas «&nbsp;_for humans_&nbsp;», explicitement «&nbsp;_for Igor_&nbsp;». Cohérent avec [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md)&nbsp;: «&nbsp;_C'est ma voiture._&nbsp;»

## Dépendances `dev`

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

| Outil                                          | Rôle dans Ocarina                                                                                                                                          |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ruff`                                         | Linter + formatter (remplace flake8 + isort + black). `select = ["ALL"]`.                                                                                  |
| `mypy` (+ extensions)                          | Type-checker. `strict = true` (cf. `mypy.ini`).                                                                                                            |
| `pytest`                                       | Runner des tests unitaires (le framework est lui-même testé).                                                                                              |
| `pytest-cov`                                   | Couverture de tests (du framework lui-même). Configurée dans `pyproject.toml#tool.coverage`.                                                               |
| `hypothesis`                                   | _Property-based testing (PBT)_&nbsp;→&nbsp;`test_invariants_properties.py`.                                                                                |
| `pytest-mypy-plugins`                          | Tests **statiques** de typage (vérifie les erreurs _mypy_ attendues et tests d'inférence de types avec `reveal_type`).                                     |
| `allure-pytest` /&nbsp;`allure-python-commons` | Rapport Allure (déployé sur GH Pages).                                                                                                                     |
| `pre-commit`                                   | Hooks Git locaux (ruff-format).                                                                                                                            |
| `syrupy`                                       | _Snapshot testing_ (sortie de `pretty_print_results`, `results_to_json`).                                                                                  |
| `selenium`                                     | Présent en `dev` parce qu'Ocarina **ne dépend pas** de Selenium pour fonctionner, livre juste un _adapter_ Selenium pour être immédiatement opérationnel.  |
| `playwright`                                   | Même logique&nbsp;: un second _adapter_ livré (depuis la `1.1.3`). Ocarina pilote désormais **Selenium et Playwright** out of the box, derrière les mêmes ports. |
| `twine` /&nbsp;`build`                         | Publication PyPI.                                                                                                                                          |
| `prysk`                                        | Tests CLI au format _cram_ (`.t`). Successeur de `cram`.                                                                                                   |

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

- **`strict = true`**&nbsp;: active `--warn-redundant-casts`, `--warn-unused-ignores`, `--no-implicit-optional`, `--check-untyped-defs`, etc.
- Deux exceptions&nbsp;: `disallow_incomplete_defs` et `disallow_untyped_defs` désactivés, car l'auteur estime que l'**inférence** de type de _mypy_ est suffisante quand on n'a pas besoin d'expliciter. Toutes les annotations explicites sont là où elles **comptent**.

## `pyproject.toml#tool.ruff`

```toml
[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "ANN002", "ANN003", "ANN201",
    "TRY003",
    "C901",
    "D203",    # conflit avec D211
    "D213",    # conflit avec D212
    "COM812",  # conflit avec le formatter ruff (auto-fix)
]

[tool.ruff]
exclude = ["**/.venv/**", "**/bin/**", "**/__init__.py", "**/__bypass_linter__"]
```

- **`select = ["ALL"]`**&nbsp;: toutes les règles de _ruff_ sont activées (~800).
- **Ignore list courte**&nbsp;: six règles seulement, toutes justifiées.
- **`B008` NE doit JAMAIS être ignoré** («&nbsp;_`# "B008",  # * ... NEVER ignore this rule without knowing very well what you are doing: https://docs.astral.sh/ruff/rules/function-call-in-default-argument/`_&nbsp;»). C'est une note pour ne pas répéter une erreur passée.
- **`**/**bypass_linter**`\*\*&nbsp;: convention de répertoire pour héberger du code explicitement non-linté (utile pour des modules expérimentaux internes).

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

| Réglage                      | Effet                                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------------------------- |
| `log_cli = true`             | Tous les logs des tests apparaissent en CLI (utile pour les scénarios qui passent par `ILogger`). |
| `--cov=src` + `--cov-branch` | Couverture par branche, pas seulement par ligne.                                                  |
| `--cov-report=html` + `xml`  | Trois sorties&nbsp;: terminal, HTML local, XML pour ingestion CI.                                 |

## `pyproject.toml#tool.coverage`

Voir le détail ici&nbsp;: [`../04-internal-tests/07-coverage-policy.md`](../04-internal-tests/07-coverage-policy.md). En bref&nbsp;: tout ce qui est _shape_ (custom_types, ports, errors), ce qui requiert un navigateur réel (adapters Selenium), et ce qui est traversé par les cram tests (cli/store, cli/builder), est explicitement omis. Pour ne pas **fausser** les métriques.

## `Makefile`

| Recette                                 | Effet                                                                                                                       |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `make install`                          | Crée `.venv` si absent, `pip install -e . --group dev`, `pre-commit install`. Cross-OS (Windows /&nbsp;autres).             |
| `make install-on-ci`                    | Variante CI&nbsp;: `pip install -r requirements-dev.txt` puis `pip install -e . --no-deps`.                                 |
| `make test`                             | `make cram-test` puis `pytest --alluredir=allure-results -vv --hypothesis-show-statistics` puis copie de `categories.json`. |
| `make cram-test`                        | `prysk tests/cram/` (sur Windows&nbsp;: ne fait rien).                                                                      |
| `make check-coding-style`               | `mypy + ruff`                                                                                                               |
| `make mypy-check`                       | `mypy src/ tests/`                                                                                                          |
| `make ruff-check`                       | `ruff check .`                                                                                                              |
| `make ruff-format`                      | `ruff format .`                                                                                                             |
| `make generate-allure`                  | `allure generate allure-results -o allure-report`                                                                           |
| `make serve-allure`                     | Ouvre le rapport Allure dans le navigateur.                                                                                 |
| `make serve-htmlcov`                    | Idem pour `htmlcov/`                                                                                                        |
| `make test-ui`                          | `make test` + `make generate-allure` + `make serve-htmlcov` + `make serve-allure`                                           |
| `make update-snapshots`                 | `pytest --snapshot-update`                                                                                                  |
| `make clean` /&nbsp;`make clean-allure` | Cleanup cross-OS.                                                                                                           |

## `categories.json` (taxonomie Allure)

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

Quatre catégories, dont par exemple _Invariant violations_&nbsp;: échecs des tests impliquant `validate(...).execute().raise_if_invalid()`

## `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.11
    hooks:
      - id: ruff-format
```

Minimal&nbsp;: juste `ruff-format` en pre-commit. Les autres outils (`ruff check`, `mypy`) sont en CI uniquement, choix qui réduit la friction locale (= éviter de «&nbsp;_casser les couilles_&nbsp;» des développeurs).

## URLs

```toml
[project.urls]
Documentation = "https://mojo-molotov.github.io/ocarina-holy-book"
Homepage      = "https://github.com/mojo-molotov/ocarina"
Issues        = "https://github.com/mojo-molotov/ocarina/issues"
```

L'URL `Documentation` pointe vers le **Holy Book**. Voir [`../09-holy-book/`](../09-holy-book/README.md)

## Build backend

```toml
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"
```

`hatchling`&nbsp;: choix moderne (PEP 517/518), léger, sans config _ad hoc_.
