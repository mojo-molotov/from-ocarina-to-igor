---
title: "02.05.06 — TestCampaign[Driver]"
description: "TestCampaign[Driver] : l'exécution ordonnée d'une séquence de suites partageant une config de workers, avec le drapeau campaign_has_failed."
weight: 6
date: 2026-05-20
series: ["orchestration"]
series_order: 6
tags: ["ocarina", "parallelisation"]
---

# 02.05.06&nbsp;—&nbsp;`TestCampaign[Driver]`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/oc_test_campaign.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_campaign.py)
>
> **Responsabilité unique**&nbsp;: exécuter une **séquence de suites** dans l'ordre, partager une config de workers, et déclarer `campaign_has_failed`.

## Code

```python
class TestCampaign[Driver]:
    def __init__(
        self,
        *,
        name: str,
        suites: Sequence[TestSuite[Driver]],
        max_workers: int,
        saturate_workers: bool | None = None,
    ) -> None:
        validate_test_suites_names(suites=suites, name="suites").execute().raise_if_invalid()

        self.name = name
        self._suites = suites
        self._results: TestCampaignResults = {}
        self._max_workers = max_workers
        self._saturate_workers = saturate_workers

        for suite in self._suites:
            suite._campaign_name = self.name

    def run_all(
        self, *, skip_all: bool = False, saturate_workers: bool = True
    ) -> TestCampaignResults:
        self._results.clear()

        resolved_saturate_workers = (
            self._saturate_workers
            if self._saturate_workers is not None
            else saturate_workers
        )

        if skip_all:
            for suite in self._suites:
                self._results[suite.name] = {
                    name: (None, -1, test_id)
                    for name, test_id in suite.test_names_and_ids
                }
            return self._results

        for suite in self._suites:
            self._results[suite.name] = suite.run(
                max_workers=self._max_workers,
                saturate_workers=resolved_saturate_workers,
            )

        return self._results


def campaign_has_failed(results: TestCampaignResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaign_results in results.values()
        for outcome, _, _ in campaign_results.values()
    )
```

## Anatomie

### Garde-fou au constructeur

```python
validate_test_suites_names(suites=suites, name="suites").execute().raise_if_invalid()
```

→ Les noms de suites de la campagne doivent être uniques&nbsp;— de façon insensible à la casse depuis `1.1.10` (NFC + casefold). Levé _dès la construction_.

### Injection du nom de campagne dans les suites

```python
for suite in self._suites:
    suite._campaign_name = self.name
```

On touche directement à `suite._campaign_name`. C'est volontaire&nbsp;: on _attache_ le nom de campagne à chaque suite pour que `TestFlow` puisse construire la taxonomie `(cycle, campaign, suite, test_name)` plus tard.

### Séquentialité

```python
for suite in self._suites:
    self._results[suite.name] = suite.run(
        max_workers=self._max_workers,
        saturate_workers=resolved_saturate_workers,
    )
```

Une suite après l'autre. La parallélisation vit dans une suite, pas entre les suites.  
→ La séquentialité inter-suites est un invariant de design, pas une limitation.

### `max_workers` est _campagne-level_

Le `max_workers` est défini une fois pour toute la campagne, partagé entre toutes ses suites. On ne veut pas qu'une suite «&nbsp;_riche_&nbsp;» ait plus de workers qu'une suite «&nbsp;_pauvre_&nbsp;». Et on permet à un projet de _scinder_ les workloads via plusieurs campagnes (ex. une campagne «&nbsp;_smoke_&nbsp;» avec 2 workers, une «&nbsp;_load_&nbsp;» avec 8).

### `skip_all=True`

```python
self._results[suite.name] = {
    name: (None, -1, test_id)
    for name, test_id in suite.test_names_and_ids
}
```

Chaque test skippé reçoit `(None, -1, test_id)`.

1. **`None`** parce qu'on **ne peut pas dire** que c'est Ok ou Fail. C'est une troisième valeur, logique, pour un skip.
2. **`-1`** comme nombre de pas de test, parce que c'est un **détrompeur** clair (régulièrement utilisé pour ça en programmation).
3. **`test_id`** conservé pour le rapport.

Invoqué par `TestCycle` quand le smoke a fail&nbsp;: «&nbsp;_skip toutes les campagnes principales avec un statut SKIPPED_&nbsp;».

## `campaign_has_failed`

```python
def campaign_has_failed(results: TestCampaignResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaign_results in results.values()
        for outcome, _, _ in campaign_results.values()
    )
```

1. `results.values()` itère sur les `TestSuiteResults` (un par suite).
2. `campaign_results.values()` itère sur les `TestSuiteResult` (un par test dans la suite).
3. `outcome, _, _` déballe `(TestResult, steps_count, test_id)`.

Le `any` court-circuite dès qu'un `Fail` est trouvé.

## Quand `TestCycle` appelle-t-il `campaign_has_failed`&nbsp;?

```python
def _run_smoke(*, fail_fast: bool) -> bool:
    failed = False
    for campaign in self._smoke_campaigns:
        results = campaign.run_all(skip_all=failed if fail_fast else False, ...)
        self._results[campaign.name] = results
        if campaign_has_failed(results):
            failed = True
    return failed
```

`campaign_has_failed` est utilisé **uniquement** par `TestCycle` pour décider de la suite (skipper les campagnes principales).

## Tableau récapitulatif

| Aspect                   | `TestCampaign`                                                 |
| ------------------------ | -------------------------------------------------------------- |
| Concurrence inter-suites | **Séquentielle**, jamais parallèle                             |
| Concurrence intra-suites | Délégué à `TestSuite` (qui parallélise avec une ThreadPool)    |
| `max_workers`            | Une seule valeur partagée                                      |
| `saturate_workers`       | Cascade `bootstrap > campaign > suite` (le plus profond gagne) |
