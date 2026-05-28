---
title: "04.01 — Stratégie « dehors comme un utilisateur »"
description: "La stratégie de test interne d'Ocarina, dehors comme un utilisateur : aucun test ne triche en regardant les internes, posée dès le conftest.py."
weight: 1
date: 2026-05-20
series: ["tests-internes"]
series_order: 1
tags: ["scenarios", "selenium"]
---

# 04.01&nbsp;—&nbsp;Stratégie «&nbsp;_dehors comme un utilisateur_&nbsp;»

> C'est la posture documentée dès le `conftest.py` des tests scénarios. Aucun test ne triche en regardant les internes.

## `tests/scenarios/conftest.py`

| Composant                                                                           | Rôle                                                                              |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `FakeDriver` (dataclass)                                                            | Driver minimaliste&nbsp;: `title`, `disposed`. Aucune méthode Selenium.           |
| `make_built_driver()`                                                               | Factory `(FakeDriver, dispose)`, soit la signature attendue par `WebDriversPool`. |
| `make_pool(max_size=2)`                                                             | `WebDriversPool[FakeDriver]` prêt à l'emploi.                                     |
| `RecordingPOM(POMBase)`                                                             | POM qui consigne ses appels et peut être configuré pour lever.                    |
| `acting(pom, step)`                                                                 | `ActionSuccess[RecordingPOM]` complet (failure+success en no-op).                 |
| `scenario_of("ok", "ok2")`                                                          | `TestScenario[FakeDriver]` à N steps.                                             |
| `failing_scenario(step="boom", exc=...)`                                            | Scénario à 1 step qui lève.                                                       |
| `make_test(name, scenario=..., test_id=..., skipped=False)`                         | `Test[FakeDriver]`                                                                |
| `make_suite(name, tests, pool=..., transient_errors=..., max_retries_per_test=...)` | `TestSuite[FakeDriver]`                                                           |
| `make_campaign(name, suites, max_workers=1)`                                        | `TestCampaign[FakeDriver]`                                                        |
| `make_cycle(name="cycle", campaigns=..., smoke=..., mode=...)`                      | `TestCycle[FakeDriver]`                                                           |
| `run_chain(runner)`                                                                 | Helper qui exécute un `ChainRunner` et retourne le `ActionChain`.                 |

## `FakeDriver`

```python
@dataclass
class FakeDriver:
    title: str = "fake"
    disposed: bool = False
```

C'est **tout**.
**Le cœur d'Ocarina n'appelle aucune API Selenium**.

Tout ce qui est appelé sur le driver est appelé par le **POM** (que l'utilisateur écrit).

Le framework lui-même ne fait que&nbsp;:

- L'acquérir via `WebDriversPool.acquire()`.
- Le passer au scénario /&nbsp;aux watchers.
- Le disposer à la fin.

Donc un `FakeDriver` _sans rien_ est suffisant pour tester l'orchestration.  
C'est la **preuve par les tests** que le framework est agnostique.

## `RecordingPOM`

```python
@dataclass
class RecordingPOM(POMBase):
    calls: list[str] = field(default_factory=list)
    raise_on: set[str] = field(default_factory=set)
    raises_with: dict[str, Exception] = field(default_factory=dict)
    _title: str = "Recording page"

    def verify(self, *, timeout=None) -> "RecordingPOM":
        return self._do("verify")

    def get_current_title(self) -> str:
        return self._title

    def step(self, name: str) -> "RecordingPOM":
        return self._do(name)

    def _do(self, name: str) -> "RecordingPOM":
        self.calls.append(name)
        if name in self.raise_on:
            raise self.raises_with.get(name, RuntimeError(f"{name} failed"))
        return self
```

C'est un _spy_.

- **Enregistre** chaque appel dans `self.calls`. Permet d'asserter _ce qui a été appelé_, dans quel ordre.
- **Peut lever** à la demande&nbsp;: `RecordingPOM(raise_on={"boom"}, raises_with={"boom": ValueError("nope")})`.
- **Retourne `self`** sur chaque appel (fluent chaining).

```python
def test_short_circuit_after_failure() -> None:
    pom = RecordingPOM(raise_on={"second"})
    runner = drive_page(
        acting(pom, "first"),
        acting(pom, "second"),
        acting(pom, "third"),
    )
    chain = runner.run()
    assert chain.has_failed()
    assert pom.calls == ["first", "second"]    # ✅ "third" jamais appelé
```

## `acting(pom, step)`

```python
def acting(pom: RecordingPOM, step: str) -> Any:
    return (
        create_act(pom, lambda p: p.step(step))
        .failure(lambda exc: None)
        .success(lambda: None)
    )
```

→ Un `ActionSuccess[RecordingPOM]` complet, avec handlers no-op. Utilisable directement dans `drive_page(...)`.

## `make_*`

`make_test`, `make_suite`, `make_campaign`, `make_cycle` instancient le framework _comme un utilisateur_. Tous prennent des _valeurs par défaut raisonnables_ (`MutedLogger`, `make_pool()`, `max_workers=1`, etc.) pour ne pas polluer les tests avec du boilerplate.

On teste l'API, pas l'interne.

## Absence de mock du framework

Aucun test n'utilise `unittest.mock`. Quelques tests `unittest.mock` apparaissent _ponctuellement_ pour _mocker du time_ ou _mocker un appel externe_, mais **jamais pour mocker une classe du framework**.

C'est la **garantie** que les tests valident le _comportement réel_ du framework, pas une supposition sur lui.

## `@allure.*`

```python
@allure.epic("Railway / action chain")
@allure.feature("Action chain")
@allure.tag("act", "error-handling")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("layer", "unit")
@allure.title("A raising action is caught into Fail; the failure handler fires with the exception")
def test_raising_act_is_captured_as_fail() -> None: ...
```

| Décorateur                       | Sens                                                                        |
| -------------------------------- | --------------------------------------------------------------------------- |
| `@allure.epic`                   | Plus haut niveau de regroupement (Allure)                                   |
| `@allure.feature`                | Sous-niveau (feature)                                                       |
| `@allure.tag`                    | Tags libres (act, error-handling, retry, etc.)                              |
| `@allure.severity`               | TRIVIAL, MINOR, NORMAL, CRITICAL, BLOCKER                                   |
| `@allure.label("layer", "unit")` | Label custom&nbsp;—&nbsp;distingue `unit` /&nbsp;`integration` /&nbsp;`e2e` |
| `@allure.title`                  | Titre humain, lisible dans le rapport                                       |

→ [Rapport allure](https://mojo-molotov.github.io/ocarina/allure-report/) (tests du framework)

## `# ruff: noqa: S101`

```python
# ruff: noqa: S101
"""Railway and action-chain behavior."""
```

`S101` interdit l'usage d'`assert` (par défaut, en production code). Dans les tests, c'est inévitable.  
`# ruff: noqa: S101` désactive cette règle **pour tout le fichier**.
