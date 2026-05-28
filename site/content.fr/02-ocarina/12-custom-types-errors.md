---
title: "02.12 — Custom types & custom errors"
description: "La couche shape d'Ocarina : types, alias, exceptions et protocols, sans aucune logique runtime, ce qui rend le DSL typé sans surcoût d'exécution."
weight: 12
date: 2026-05-20
series: ["ocarina"]
series_order: 12
tags: ["scenarios", "selenium"]
---

# 02.12&nbsp;—&nbsp;Custom types & custom errors

> Couche _shape_ d'Ocarina. Aucune logique&nbsp;: juste des types, des alias, des exceptions, des protocols. C'est ce qui rend le DSL typé sans logique runtime additionnelle.

## `custom_types/`

| Fichier                          | Contenu                                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `effect.py`                      | `type Effect = Callable[[], None]` + `type Effects = tuple[Effect, ...]`                                 |
| `thunk.py`                       | `type Thunk[T] = Callable[[], T]`                                                                        |
| `tpom.py`                        | `TypeVar TPOM bound POMBase`                                                                             |
| `supports_write.py`              | `Protocol SupportsWrite[T]` (`write(s: T) -> Any`)                                                       |
| `built_web_driver.py`            | `type BuiltWebDriver[Driver] = tuple[Driver, Effect]`                                                    |
| `scenario.py`                    | `Scenario[Driver]` (frozen dataclass)                                                                    |
| `test_components.py`             | `TestChain`, `TestSetup`, `TestTeardown`, `TestWatchers[Driver]`                                         |
| `test_runner.py`                 | `TestRunner[Driver]` (frozen dataclass)                                                                  |
| `oc_test.py`                     | `TestName`, `TestScenario[Driver]`, `TestScenarioFragment[Driver]`                                       |
| `oc_test_layers.py`              | `TestId`, `TestResult`, `TestSuiteResult`, `TestSuiteResults`, `TestCampaignResults`, `TestCycleResults` |
| `selenium/built_web_driver.py`   | `BuiltSeleniumWebDriver = BuiltWebDriver[WebDriver]`                                                     |
| `selenium/oc_test_scenario.py`   | `SeleniumTestScenario = TestScenario[WebDriver]`                                                         |
| `selenium/supported_browsers.py` | `type SupportedSeleniumBrowser = Literal["chrome", "firefox", "edge", "safari"]`                         |
| `selenium/web_drivers_pool.py`   | `type SeleniumWebDriversPool = WebDriversPool[WebDriver]`                                                |

Tous ces fichiers sont _excluded de la couverture_ (`pyproject.toml#tool.coverage`)&nbsp;:

```toml
"src/ocarina/custom_types/*",
```

Raison&nbsp;: aucune logique runtime à tester&nbsp;; ce sont des _shapes_.

## Hiérarchie

```python
# src/ocarina/custom_types/oc_test_layers.py

type TestId = str
type _TestStepsCount = int
type TestResult = Result[Any] | None
type TestSuiteResult = tuple[TestResult, _TestStepsCount, TestId]
type TestSuiteResults = dict[str, TestSuiteResult]                  # {test_name: TestSuiteResult}
type TestCampaignResults = dict[str, TestSuiteResults]              # {suite_name: TestSuiteResults}
type TestCycleResults = dict[str, TestCampaignResults]              # {campaign_name: TestCampaignResults}
```

Lecture&nbsp;:

```
TestCycleResults
  └── "Dashboard login" (campaign)
      └── "Login happy paths" (suite)
          ├── "Login - without OTP" (test) → (Ok(None), 15, "login_no_otp")
          └── "Login - with OTP"    (test) → (Fail(exc), 8, "login_otp")
```

Trois niveaux de nesting, indexés par nom. Le `(TestResult, steps_count, test_id)` est la feuille.

## `Scenario[Driver]`, `TestRunner[Driver]`, `TestChain`

```python
@dataclass(frozen=True)
class Scenario[Driver]:
    test_chain: TestChain
    setup: TestSetup = field(default=None)
    teardown: TestTeardown = field(default=None)
    watchers: TestWatchers[Driver] | None = field(default=None)


@dataclass(frozen=True)
class TestRunner[Driver]:
    chain_runners: list[ChainRunner[Any]]
    skipped: bool
    setup: Effect | None
    teardown: Effect | None
    watchers: Sequence[Watcher[Driver]] | None


type TestChain = Sequence[ChainRunner[Any]]
type TestSetup = Effect | None
type TestTeardown = Effect | None
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

Deux dataclasses + 4 type aliases. Pas de méthode, juste des bags de données.

## `custom_errors/`

| Fichier                                | Exception                | Levée par                                                                                                                                                                                            |
| -------------------------------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_framework/no_matching_branch.py` | `NoMatchingBranchError`  | `match_page` quand aucun `when` ne match                                                                                                                                                             |
| `test_framework/pages.py`              | `PageVerificationError`  | Conventionnellement levée par `POM.verify` quand la page n'est pas la bonne                                                                                                                          |
| `test_framework/driver_died.py`        | `DriverDiedError`        | `driver_healthcheck` quand le driver ne répond plus                                                                                                                                                  |
| `test_framework/campaigns.py`          | `DuplicateTestNameError` | Levée quand deux tests d'une même campagne portent le même `name`. Sous-classe de `DuplicatesError` (lui-même `InvariantViolationError`)&nbsp;; transporte la séquence `duplicates` pour le rapport. |

## `DriverDiedError`

```python
@final
class DriverDiedError(Exception):
    """Raised when a WebDriver instance dies or becomes unresponsive."""
```

→ Permet à un appelant de distinguer «&nbsp;_le driver est mort_&nbsp;» de «&nbsp;_le driver fait quelque chose d'inattendu_&nbsp;». Ocarina la traite comme transient via les adapters projet (le projet ajoute `DriverDiedError` dans son `transient_errors`).

## `PageVerificationError`

Conventionnellement levée dans `POM.verify`&nbsp;:

```python
def verify(self, *, timeout: float | None = None) -> Self:
    try:
        WebDriverWait(self._driver, timeout or get_timeout()).until(...)
    except TimeoutException as exc:
        raise PageVerificationError from exc
    return self
```

Permet de distinguer «&nbsp;_la page n'est pas la bonne_&nbsp;» de «&nbsp;_il y a eu une erreur Selenium_&nbsp;».

## `NoMatchingBranchError`

Levée par `_match_page_builder` quand aucun `when` ne match. Voir [`03-railway/07-match-page-when.md`](03-railway/07-match-page-when.md)

C'est une erreur de _logique de scénario_&nbsp;: ça veut dire que l'utilisateur a oublié de couvrir un cas. Elle devrait être propagée en `Fail` sur le rail d'échec, pas dans `transient_errors`, parce que retry ne corrigera pas le manque de couverture.

## `custom_invariants/testing/`

| Fichier                      | Invariant                     | Lève sur                                           |
| ---------------------------- | ----------------------------- | -------------------------------------------------- |
| `workers.py`                 | `validate_workers_amount`     | `workers < 1`                                      |
| `oc_test_runners_ids.py`     | `validate_test_runners_ids`   | IDs en doublon                                     |
| `oc_test_runners_names.py`   | `validate_test_runners_names` | Noms en doublon OU invalides en tant que filenames |
| `oc_test_suites_names.py`    | `validate_test_suites_names`  | Noms de suites en doublon                          |
| `oc_test_campaigns_names.py` | `validate_campaigns_names`    | Noms de campagnes en doublon                       |
| `oc_test_cycles_names.py`    | `validate_test_cycle_name`    | Invalide en tant que filename                      |

Tous écrits avec `FrameworkInvariantValidator.create(...)` (cf. [`04-invariants/05-business-vs-framework-validator.md`](04-invariants/05-business-vs-framework-validator.md)).

## `SupportsWrite[T]`

```python
from typing import Protocol, TypeVar

T_contra = TypeVar("T_contra", contravariant=True)

class SupportsWrite(Protocol[T_contra]):
    def write(self, s: T_contra, /) -> Any: ...
```

Protocol minimaliste&nbsp;: tout objet avec `.write(s)` est utilisable. Permet aux loggers de prendre un `stream: SupportsWrite[str] | None` (sys.stdout, sys.stderr, fichier, BytesIO mocké).

Note&nbsp;: `contravariant=True` parce qu'`écrire` est une opération _input_, donc contravariant en `T`.  
Conforme à la stdlib de Python.
