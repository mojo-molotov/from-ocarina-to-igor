---
title: "02.05.05 — Saturation des workers"
description: "La saturation des workers : le clonage aléatoire des tests d'une suite jusqu'au nombre de workers, pour que les succès ne doivent rien au hasard."
weight: 5
date: 2026-05-20
series: ["orchestration"]
series_order: 5
tags: ["ocarina", "parallelisation"]
---

# 02.05.05&nbsp;—&nbsp;Saturation des workers

> Mécanisme propre à Ocarina&nbsp;: si une suite a moins de tests que de workers disponibles, **on clone aléatoirement** des tests jusqu'à atteindre le nombre de workers. Les copies sont renommées `[COPY 1] <name>`, `[COPY 2] <name>`, etc.

## Pourquoi

Le Holy Book formalise la motivation dans le chapitre «&nbsp;_Premiers obstacles du monde réel_&nbsp;»&nbsp;:

> Son option `saturate_workers` permet de forcer du clonage aléatoire de tests à l'intérieur d'une suite.
>
> Dès lors qu'il y a plus de _workers_ disponibles dans la _DriversPool_ que de tests à exécuter dans une suite, Ocarina va alors cloner les tests aléatoirement, démarrer tous les drivers, et tous leur assigner un test à effectuer.

Et la finalité&nbsp;:

> Au-delà des problématiques de concurrence, ce mécanisme de clonage vise également à s'assurer que les tests en succès ne doivent rien au hasard. Cet effet est amplifié par le degré de scaling horizontal et le nombre de workers impliqués.

Deux bénéfices distincts&nbsp;:

1. **Détection des _heisenbugs_ de concurrence**. Si un test a une race condition, il a plus de chances de se manifester quand il tourne N fois en parallèle.
2. **Anti-hasard**. Si un test passe N fois en parallèle, il ne passe pas _par chance_.

## Code

```python
def _prepare_tests_for_saturated_threading(
    self, max_workers: int
) -> Sequence[Test[Driver]]:
    base_tests = list(self._tests)

    if len(base_tests) == 0:
        return base_tests

    extra_tests: list[Test[Driver]] = []
    copy_counters: dict[str, int] = {}

    for _ in range(max_workers - len(base_tests)):
        original = random.choice(base_tests)  # noqa: S311
        copy_counters.setdefault(original.name, 0)
        copy_counters[original.name] += 1

        cloned = copy.copy(original)
        space = " " if self._put_space_after_copy_indicator else ""
        cloned.name = (
            f"[{self._copy_indicator}{space}{copy_counters[original.name]}]"
            f" {original.name}"
        )
        extra_tests.append(cloned)

    return base_tests + extra_tests
```

1. **Liste de base**&nbsp;: conversion en `list` (mutation).
2. **Court-circuit si vide**&nbsp;: possible avec `--only` ou `--exclude` qui auraient vidé la suite, d'où ce check.
3. **Boucle** `max_workers - len(base_tests)`&nbsp;:
   - **`random.choice(base_tests)`**&nbsp;: sélection aléatoire (un même test peut être cloné plusieurs fois).
   - **`copy.copy(original)`**&nbsp;: copie shallow. Le scénario factory est partagé (référence), mais le `name` peut être modifié. C'est permis grâce à l'IoC + le fait que les scénarios doivent être **idempotents by-design**.
   - **Renommage**&nbsp;: `[COPY 1] <name>`, `[COPY 2] <name>`. Le compteur est par-test.
4. **Retour**&nbsp;: `base + extras`.

Notes&nbsp;:

- **`# noqa: S311`**&nbsp;: ruff alerte sur `random.choice` (non cryptographique). C'est volontaire&nbsp;: on n'a pas besoin de hasard crypto, juste de variation.
- **`copy.copy(original)`** suffit. `copy.deepcopy` serait excessif&nbsp;: on veut juste un nouveau wrapper avec un autre `name`, pas dupliquer la factory de scénario. C'est suffisamment bien fait pour marcher en étant très léger.

## `saturate_workers`

Le paramètre `saturate_workers` peut être réglé à **trois endroits** différents&nbsp;:

| Niveau         | Source                               | Effet                    |
| -------------- | ------------------------------------ | ------------------------ |
| `bootstrap`    | `bootstrap(saturate_workers=...)`    | Default global           |
| `TestCampaign` | `TestCampaign(saturate_workers=...)` | Surcharge le `bootstrap` |
| `TestSuite`    | `TestSuite(saturate_workers=...)`    | Surcharge la campagne    |

Règle&nbsp;: **le plus profond gagne**. Tiré du Holy Book&nbsp;:

> Il est aussi possible de l'activer ou de la désactiver individuellement, soit au niveau d'une suite, soit au niveau d'une campagne. En cas de contradiction, c'est l'élément le plus profond de l'arborescence qui a le dernier mot. Par exemple, si une campagne dit de désactiver l'option, mais qu'une suite dit de l'activer, alors la suite prend la priorité.

Mécaniquement, dans `TestSuite.run`&nbsp;:

```python
resolved_saturate_workers = (
    self._saturate_workers
    if self._saturate_workers is not None
    else saturate_workers
)
```

Si la suite a un `_saturate_workers` non-None (set explicite à `True` ou `False`), on l'utilise. Sinon, on prend la valeur transmise par la campagne (qui suit la même règle face au bootstrap).

## Cas d'usage&nbsp;: révéler des problèmes de concurrence

Une suite avec **un seul test** + `--workers 3` + `saturate_workers=True`&nbsp;:

```
base_tests = [test_login]                 # 1 test
max_workers = 3
extras = [
    [COPY 1] test_login,                  # même factory, autre wrapper
    [COPY 2] test_login,                  # idem
]
tests = [test_login, [COPY 1] test_login, [COPY 2] test_login]
```

Tous les 3 sont dispatch sur 3 drivers _parallélisés_. Si `test_login` a une race condition (par exemple un cache local non-thread-safe), elle se révèle.

## Cas d'usage&nbsp;: maximiser le ciblage

Le Holy Book mentionne&nbsp;:

> Il est possible de temporairement créer une suite avec seulement un test pour maximiser le ciblage.

Pattern&nbsp;: on **isole** un test problématique dans sa propre suite, on règle `--workers N`, on laisse `saturate_workers=True`. On clone N copies du test, on bombarde, on voit ce qui sort.

## Cas d'usage&nbsp;: tests data-driven déjà nombreux

Si une suite a déjà 12 tests data-driven et `--workers 3`, **pas de saturation**&nbsp;: `12 > 3`, on a déjà plus de tests que de workers, la boucle ne fait rien.

```python
for _ in range(max_workers - len(base_tests)):   # range(3 - 12) = range(-9) = empty
    ...
```

## `[COPY 1]`, `[COPY 2]`, … vs `[+1]`, `[+2]`, …

Le `copy_indicator` est paramétrable&nbsp;:

```python
TestSuite(
    copy_indicator="+",
    put_space_after_copy_indicator=False,
    ...
)
```

→ Les copies seraient nommées `[+1] <name>`, `[+2] <name>`. C'est ce que fait l'adapter projet `ocarina-example` pour des logs plus compacts (cf. [`../../07-ocarina-example/02-adapters.md`](../../07-ocarina-example/02-adapters.md)).

## La CI le note explicitement

Le `CLAUDE.md` d'`ocarina-with-ai-example`&nbsp;:

> With `--workers N`, Ocarina duplicates single-test suites up to N times to flush concurrency hazards (race conditions, session cleanup, driver reuse). The `[COPY N]` annotations are not noise&nbsp;—&nbsp;they confirm the saturation framework is active. Expect them on small smoke suites; this is a feature.
