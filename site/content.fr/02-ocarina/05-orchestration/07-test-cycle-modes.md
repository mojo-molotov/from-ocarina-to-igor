---
title: "02.05.07 — TestCycle[Driver] + modes"
weight: 7
date: 2026-05-20
series: ["orchestration"]
series_order: 7
tags: ["ocarina"]
---

# 02.05.07&nbsp;—&nbsp;`TestCycle[Driver]` + modes

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/oc_test_cycle.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_cycle.py)
>
> **Responsabilité unique**&nbsp;: orchestrer les campagnes _smoke_ puis _main_, et appliquer un mode de gestion d'échec des smoke.

## Deux modes

```python
type Mode = Literal[
    "fail-fast-on-first-smoke-campaigns-sequence-fail",
    "wait-for-all-smoke-tests",
]
```

| Mode                                                        | Comportement                                                                                               |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `fail-fast-on-first-smoke-campaigns-sequence-fail` (défaut) | Dès qu'une campagne de smoke fail, les **suivantes** sont _skippées_.                                      |
| `wait-for-all-smoke-tests`                                  | **Toutes** les campagnes de smoke s'exécutent. Si _au moins une_ fail, les campagnes _main_ sont skippées. |

| Cas                                                                           | Mode                                                 |
| ----------------------------------------------------------------------------- | ---------------------------------------------------- |
| Smoke par dépendance (par exemple&nbsp;: "login" puis "dashboard accessible") | `fail-fast` (si login échoue, dashboard est inutile) |
| Smoke parallèles (par exemple&nbsp;: "homepage" + "API ping")                 | `wait-for-all` (on veut voir les deux)               |

Le default est `fail-fast` parce que c'est le cas le plus fréquent.

## Code

```python
@final
class TestCycle[Driver]:
    def __init__(
        self,
        *,
        name: str,
        campaigns: Sequence[TestCampaign[Driver]],
        smoke_tests_campaigns: Sequence[TestCampaign[Driver]] | None = None,
        mode: Mode | None = None,
    ) -> None:
        if mode is None:
            mode = "fail-fast-on-first-smoke-campaigns-sequence-fail"

        smoke_campaigns = smoke_tests_campaigns or []
        all_campaigns = [*smoke_campaigns, *campaigns]

        for campaign in all_campaigns:
            for suite in campaign._suites:
                chain_validations(
                    validate_test_cycle_name(cycle_name=name, name="test_cycle"),
                    validate_campaigns_names(campaigns=all_campaigns, name="all campaigns (smoke + deep tests)"),
                    validate_test_suites_names(suites=campaign._suites, name="suites"),
                    validate_test_runners_names(tests=suite._tests, name="tests"),
                ).execute().raise_if_invalid()

        self.name = name
        self._campaigns = campaigns
        self._smoke_campaigns = smoke_campaigns
        self._results: TestCycleResults = {}
        self._mode = mode

        # Injection du nom de cycle dans toutes les suites
        for campaign in self._campaigns:
            for suite in campaign._suites:
                suite._cycle_name = name
        for smoke_campaign in self._smoke_campaigns:
            for suite in smoke_campaign._suites:
                suite._cycle_name = name


    def run_all(self, *, saturate_workers: bool = True) -> TestCycleResults:
        self._results.clear()

        def _run_smoke(*, fail_fast: bool) -> bool:
            failed = False
            for campaign in self._smoke_campaigns:
                results = campaign.run_all(
                    skip_all=failed if fail_fast else False,
                    saturate_workers=saturate_workers,
                )
                self._results[campaign.name] = results
                if campaign_has_failed(results):
                    failed = True
            return failed

        dispatch: dict[Mode, Thunk[bool]] = {
            "fail-fast-on-first-smoke-campaigns-sequence-fail":
                lambda: _run_smoke(fail_fast=True),
            "wait-for-all-smoke-tests":
                lambda: _run_smoke(fail_fast=False),
        }

        skip_all = dispatch[self._mode]()

        for campaign in self._campaigns:
            self._results[campaign.name] = campaign.run_all(
                skip_all=skip_all, saturate_workers=saturate_workers
            )

        return self._results


def has_test_cycle_failed(results: TestCycleResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaigns in results.values()
        for tests in campaigns.values()
        for outcome, _, _ in tests.values()
    )
```

## Invariants de construction

```python
chain_validations(
    validate_test_cycle_name(cycle_name=name, name="test_cycle"),
    validate_campaigns_names(campaigns=all_campaigns, name="..."),
    validate_test_suites_names(suites=campaign._suites, name="suites"),
    validate_test_runners_names(tests=suite._tests, name="tests"),
).execute().raise_if_invalid()
```

1. **`name`** est un nom de cycle valide (cross-OS filename).
2. **Noms uniques + valides** parmi toutes les campagnes (smoke + main).
3. **Noms uniques + valides** parmi les suites de chaque campagne.
4. **Noms uniques + valides** parmi les tests de chaque suite.

Levé _à la construction_.  
Si l'utilisateur a une collision ou un nommage invalide, il l'apprend immédiatement.

## Sélection de mode via dispatch table

```python
dispatch: dict[Mode, Thunk[bool]] = {
    "fail-fast-on-first-smoke-campaigns-sequence-fail":
        lambda: _run_smoke(fail_fast=True),
    "wait-for-all-smoke-tests":
        lambda: _run_smoke(fail_fast=False),
}

skip_all = dispatch[self._mode]()
```

Pattern fonctionnel&nbsp;: on indexe une table de _thunks_ par la valeur du `Literal`. Le checker peut vérifier l'exhaustivité de la table par rapport au `Literal` (`Mode = Literal["a", "b"]`&nbsp;→&nbsp;table doit avoir les 2 clés).

> ⚠️ **Limite Python actuelle**&nbsp;: à l'heure où l'on écrit ces lignes, le type checker Python **ne vérifie pas réellement** l'exhaustivité de ce pattern (ce qu'on aurait en TypeScript avec un `Record<Mode, ...>` exhaustif). C'est une **limitation acceptée**, à documenter, pas une feature à corriger. Si on ajoute un membre au `Literal` et qu'on oublie de l'ajouter au dispatch, mypy ne le criera pas (c'est ballot). De plus, l'idiome `match` de Python a le même comportement non exhaustif.&nbsp;:'(

## _Flux complet_ d'un cycle

```
TestCycle.run_all(saturate_workers=True)
       │
       ▼
   dispatch[mode]()                           ▶︎  _run_smoke(fail_fast=<bool>)
       │
       │  for campaign in self._smoke_campaigns :
       │     results = campaign.run_all(skip_all=failed if fail_fast else False, ...)
       │           │
       │           ▼
       │     pour chaque suite :
       │       suite.run(max_workers=...) → dict[test_name -> TestSuiteResult]
       │
       │     self._results[campaign.name] = results
       │     if campaign_has_failed(results) :
       │         failed = True
       │
       └─ return failed   →  skip_all
       │
       ▼
   for campaign in self._campaigns :
       results = campaign.run_all(skip_all=skip_all, ...)
       self._results[campaign.name] = results
       │
       ▼
   return self._results
```

## `has_test_cycle_failed`

```python
def has_test_cycle_failed(results: TestCycleResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaigns in results.values()
        for tests in campaigns.values()
        for outcome, _, _ in tests.values()
    )
```

1. `results.values()`&nbsp;: itère sur les `TestCampaignResults` (un par campagne).
2. `campaigns.values()`&nbsp;: itère sur les `TestSuiteResults` (un par suite).
3. `tests.values()`&nbsp;: itère sur les `TestSuiteResult` (un par test).

Court-circuit sur le premier `Fail` trouvé.

C'est ce que le `main.py` de l'utilisateur appelle dans son `post_exec`&nbsp;:

```python
def _post_exec(results: TestCycleResults) -> None:
    print()
    pretty_print_results(results, with_colors=True)
    if has_test_cycle_failed(results):
        sys.exit(1)
```

## Pourquoi `mode` est facultatif

Le default `"fail-fast-..."` couvre 80% des cas.

L'exemple `ocarina-example` utilise `wait-for-all-smoke-tests` parce qu'il a deux campagnes smoke (`global_smoke_tests` + `corsicamon_smoke`) qui sont _indépendantes_, on veut voir les deux fail si elles fail.

L'exemple `ocarina-with-ai-example` reste sur le default (fail-fast) parce qu'il n'a qu'une campagne smoke (`prerequisites`).
