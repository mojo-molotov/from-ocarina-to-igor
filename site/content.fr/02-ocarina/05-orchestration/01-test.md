---
title: "02.05.01 — Test[Driver]"
description: "La classe Test[Driver] d'Ocarina : unité d'orchestration de base, avec spawn, fragments pre et post, et gestion du skip."
weight: 1
date: 2026-05-20
series: ["orchestration"]
series_order: 1
tags: ["ocarina", "scenarios", "selenium"]
---

# 02.05.01&nbsp;—&nbsp;`Test[Driver]`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/oc_test.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test.py)

## Signature

```python
@final
class Test[Driver]:
    def __init__(
        self,
        *,
        name: TestName,
        test_id: str | None = None,
        test_scenario: TestScenario[Driver],
        pre_test_scenarios_fragments: Sequence[TestScenarioFragment[Driver]] | None = None,
        post_test_scenarios_fragments: Sequence[TestScenarioFragment[Driver]] | None = None,
        skipped: bool = False,
    ) -> None:
        if test_id is None:
            test_id = name
        self.name = name
        self.test_id = test_id
        self._test_scenario = test_scenario
        self._pre_test_scenarios_fragments = pre_test_scenarios_fragments or []
        self._post_test_scenarios_fragments = post_test_scenarios_fragments or []
        self._skipped = skipped
```

Six paramètres&nbsp;:

| Paramètre                       | Type                                                                             | Rôle                                                                                                                       |
| ------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `name`                          | `TestName` (`str`)                                                               | Label humain&nbsp;; apparaît dans le rapport, et **devient le nom du fichier de log** (donc soumis à `is_valid_filename`). |
| `test_id`                       | `str \| None`                                                                    | Identifiant stable pour `--only` /&nbsp;`--exclude`. Si absent&nbsp;: prend `name`.                                        |
| `test_scenario`                 | `TestScenario[Driver]` (alias = `Callable[[Driver, ILogger], Scenario[Driver]]`) | _Factory_ qui construit le `Scenario` au moment de l'exécution.                                                            |
| `pre_test_scenarios_fragments`  | `Sequence[TestScenarioFragment[Driver]] \| None`                                 | Fonctions `(driver, logger) -> TestChain` exécutées **avant** le scénario principal.                                       |
| `post_test_scenarios_fragments` | `Sequence[TestScenarioFragment[Driver]] \| None`                                 | Fonctions `(driver, logger) -> TestChain` exécutées **après** le scénario principal.                                       |
| `skipped`                       | `bool`                                                                           | Si `True`, le test est enregistré mais pas exécuté.                                                                        |

### 1. `@final`

Pas d'héritage utilisateur. Si l'on veut un test «&nbsp;_spécial_&nbsp;», on _compose_ via les fragments ou via un scénario, on ne sous-classe pas.

### 2. `*` (keyword-only)

Tous les paramètres sont keyword-only.

```python
Test(
    name="Login - without OTP",
    test_id="login_no_otp",
    test_scenario=lambda driver, logger: Scenario(test_chain=...),
    pre_test_scenarios_fragments=[],
    skipped=False,
)
```

### 3. `test_id is None → test_id = name`

Dans tous les cas, on a besoin d'un ID. Mais si on n'est pas interfacé à un système qui exige un ID distinct du nom, le `name` fait l'affaire, l'unicité des `name` est de toute façon vérifiée.

### 4. `pre_test_scenarios_fragments or []`

Le `or []` permet de passer `None`. La séquence par défaut est `[]`, pas un `tuple`, mais c'est traité comme une `Sequence`. `Sequence` est immutable, ce qui rend le type checker d'autant plus strict.

### 5. Pas de `_driver` ni de `_logger`

Les dépendances runtime sont injectées par `spawn`, pas par `__init__`. Cela garantit qu'un `Test` est une **valeur**&nbsp;: on peut le sérialiser, le mocker, le passer en argument sans aucun contexte d'exécution.

## `spawn(driver, logger) -> TestRunner[Driver]`

```python
def spawn(self, driver: Driver, logger: ILogger) -> TestRunner[Driver]:
    chain_runners: list[ChainRunner[Any]] = []

    for pre_chain in self._pre_test_scenarios_fragments:
        chain_runners.extend(pre_chain(driver, logger))

    scenario = self._test_scenario(driver, logger)
    chain_runners.extend(scenario.test_chain)

    for post_chain in self._post_test_scenarios_fragments:
        chain_runners.extend(post_chain(driver, logger))

    return TestRunner(
        chain_runners=chain_runners,
        skipped=self._skipped,
        setup=scenario.setup,
        teardown=scenario.teardown,
        watchers=scenario.watchers,
    )
```

1. **Fragments pre**&nbsp;: toutes les chaînes concernées sont concaténées dans `chain_runners`.
2. **Scénario principal**&nbsp;: `self._test_scenario(driver, logger)` retourne un `Scenario[Driver]`. Sa `test_chain` est concaténée _ici_.
3. **Fragments post**&nbsp;: chaque fragment est appelé `(driver, logger) -> TestChain`&nbsp;; toutes les chaînes sont concaténées à la suite.

Le résultat est un `TestRunner` qui contient _tout_ ce qu'il faut pour l'exécution&nbsp;: la chaîne complète, le `setup`, le `teardown`, les `watchers`, et le drapeau `skipped`.

## La forme `(driver, logger) -> TestChain` pour les fragments

C'est exactement la signature d'un `test_scenario` mais qui retourne directement un `TestChain` (et pas un `Scenario`). Pourquoi cette différence&nbsp;?

| Différence                                                                     | Raison                                                                                                                        |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Un fragment **n'a pas de** `setup` /&nbsp;`teardown` /&nbsp;`watchers` propres | Les fragments sont _de la glue_&nbsp;—&nbsp;ils s'attendent à utiliser le `setup`/`teardown`/`watchers` du scénario principal |
| Un fragment **est concaténé** plutôt qu'**imbriqué**                           | La chain final est `[pre.chain..., scenario.chain..., post.chain...]`, plat                                                   |

Le `CLAUDE.md` du projet IA détaille le pattern&nbsp;:

> Reusable pre/post-conditions live under `src/tests/scenarios/_fragments/`. Wire them via:
>
> - `pre_test_scenarios_fragments=[fragment_fn, ...]`&nbsp;—&nbsp;before the main scenario chain.
> - `post_test_scenarios_fragments=[fragment_fn, ...]`&nbsp;—&nbsp;after.
>
> A fragment has the scenario shape `(driver: WebDriver, logger: ILogger) -> list[ChainRunner]`. The framework concatenates pre + scenario + post into one `ChainRunner` sequence.

Exemple&nbsp;: `login_as_demo_user`&nbsp;—&nbsp;voir [`../../08-ai-example/`](../../08-ai-example/README.md)

## `TestRunner[Driver]`

```python
# src/ocarina/custom_types/test_runner.py
@dataclass(frozen=True)
class TestRunner[Driver]:
    chain_runners: list[ChainRunner[Any]]
    skipped: bool
    setup: Effect | None
    teardown: Effect | None
    watchers: Sequence[Watcher[Driver]] | None
```

Frozen dataclass, immutable, juste un agrégateur de données. C'est ce que consomme `TestExecutor`.

## Quand utiliser le `skipped=True`

Le `skipped` flag est un échappatoire&nbsp;:

- Pour les tests «&nbsp;_WIP_&nbsp;» qui ne doivent pas tourner mais doivent rester documentés.
- Pour les tests temporairement cassés (avec ticket en regard, idéalement référencé dans le nom&nbsp;: `name="[WIP] Some test"`).

Le `Test.skipped` est lu par `TestExecutor.execute`. Si `True`, il renvoie immédiatement un `ExecutionOutcome(skipped=True)`.

À noter&nbsp;: on peut aussi _skipper dynamiquement_ via `--exclude <test_id>` ou via `--only` (cf. [`08-filter-tests-by-ids.md`](08-filter-tests-by-ids.md)). Subtilité ici&nbsp;: les tests non ciblés sont **détruits** plutôt que vraiment "skippés". Ils n'apparaissent donc pas explicitement comme _skipped_, le cycle de tests est simplement **rétréci**.

## La factory `create_selenium_test`

`src/ocarina/dsl/testing/selenium/create_test.py` fournit une factory Selenium-aware&nbsp;:

```python
def create_selenium_test(
    *,
    name: TestName,
    test_id: str | None = None,
    test_scenario: TestScenario[WebDriver],
    pre_test_scenarios_fragments: Sequence[TestScenarioFragment[WebDriver]] | None = None,
    post_test_scenarios_fragments: Sequence[TestScenarioFragment[WebDriver]] | None = None,
    skipped: bool = False,
):
    return Test(
        name=name,
        test_id=test_id,
        test_scenario=test_scenario,
        pre_test_scenarios_fragments=pre_test_scenarios_fragments,
        post_test_scenarios_fragments=post_test_scenarios_fragments,
        skipped=skipped,
    )
```

Juste un alias typé `Driver = WebDriver`. Permet aux call-sites de ne pas avoir à écrire `Test[WebDriver](...)` à chaque test.
