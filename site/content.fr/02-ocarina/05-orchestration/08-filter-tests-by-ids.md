---
title: "02.05.08 — filter_tests_by_ids"
description: "filter_tests_by_ids : le filtrage des tests d'une suite via les flags CLI only et exclude, mutuellement exclusifs."
weight: 8
date: 2026-05-20
series: ["orchestration"]
series_order: 8
tags: ["ocarina"]
---

# 02.05.08&nbsp;—&nbsp;`filter_tests_by_ids`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/filter_tests_by_ids.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/filter_tests_by_ids.py)
>
> Utilisé par `TestSuite.__init__` pour appliquer les flags CLI `--only <ids>` et `--exclude <ids>`. Mutex&nbsp;: on ne peut pas passer les deux.

## Code

```python
def filter_tests_by_ids[Driver](
    tests: Sequence[Test[Driver]],
    *,
    only: Iterable[str] = (),
    exclude: Iterable[str] = (),
    logger: ILogger,
) -> Sequence[Test[Driver]]:
    only_set = set(only)
    exclude_set = set(exclude)

    if only_set and exclude_set:
        raise ValueError("--only and --exclude cannot be used together")

    known_ids = {test.test_id for test in tests}

    if only_set:
        matched = only_set & known_ids
        if matched:
            joined = ", ".join(sorted(matched))
            logger.info(f"--only: matched test IDs: {joined}")
        return [test for test in tests if test.test_id in only_set]

    if exclude_set:
        matched = exclude_set & known_ids
        if matched:
            joined = ", ".join(sorted(matched))
            logger.info(f"--exclude: matched test IDs: {joined}")
        return [test for test in tests if test.test_id not in exclude_set]

    return tests
```

## Quatre garanties

### 1. Mutex `--only` /&nbsp;`--exclude`

```python
if only_set and exclude_set:
    raise ValueError("--only and --exclude cannot be used together")
```

Tenter de passer les deux est une erreur _runtime_ (pas une erreur _mypy_). Sémantiquement, ça n'aurait pas de sens&nbsp;: «&nbsp;_ne garder que A, B_&nbsp;» ET «&nbsp;_exclure C, D_&nbsp;»&nbsp;? Qu'est-ce que c'est que ces putains de conneries (à l'échelle d'une CLI)&nbsp;? Le mutex évite l'ambiguïté.

Cette contrainte est formalisée côté CLI dans `_create_validate_only_exclude_mutex_effect` (cf. [`../11-opinionated/03-selenium-cli.md`](../11-opinionated/03-selenium-cli.md)). Donc l'utilisateur voit le message d'erreur _avant_ que la suite ne soit construite.

### 2. _Silent ignore_ des IDs inconnus

Si l'utilisateur passe `--only test_login,test_typo` et que `test_typo` n'existe pas (typo dans le nom), Ocarina **ignore silencieusement** `test_typo`&nbsp;:

```python
return [test for test in tests if test.test_id in only_set]
```

Aucun match pour `test_typo`&nbsp;→&nbsp;il n'apparaît tout simplement pas. Pas d'erreur, pas de warning.

L'argument explicité dans le docstring&nbsp;:

> Unknown IDs (not matching any test.test_id) are silently ignored, so a typo in a CI script does not break the run.

→ C'est un choix pragmatique&nbsp;: une CI qui «&nbsp;_ne casse pas pour une typo_&nbsp;» est plus _robuste_ qu'une CI qui exige des IDs parfaits.

### 3. Log des IDs matchés

```python
matched = only_set & known_ids
if matched:
    joined = ", ".join(sorted(matched))
    logger.info(f"--only: matched test IDs: {joined}")
```

```
Login happy paths: filtering tests... --only: matched test IDs: login_no_otp, login_otp
```

Triées, séparées par `,`. Au cas où l'utilisateur passe 20 IDs, c'est lisible.

### 4. Si ni `only` ni `exclude`&nbsp;→&nbsp;on retourne `tests` tel quel

```python
return tests
```

`TestSuite(... only_ids=(), exclude_ids=())` n'introduit **aucune copie** ni **aucun overhead**. C'est le cas par défaut.

## Logger préfixé

```python
logger=create_logger().set_prefix(lambda: f"{self.name}: filtering tests...")
```

→ Le log devient `Login happy paths: filtering tests... --only: ...`. Le préfixe est **paresseux** (`Thunk[str]`), recalculé à chaque log. Voir [`../09-ports.md`](../09-ports.md), section `ILogger.set_prefix`.

## Intégration dans `TestSuite.__init__`

```python
# in TestSuite.__init__
self._tests = filter_tests_by_ids(
    tests,
    only=only_ids,
    exclude=exclude_ids,
    logger=create_logger().set_prefix(
        lambda: f"{self.name}: filtering tests..."
    ),
)
```

Le filtrage est fait **à la construction de la suite**, pas à l'exécution.

- Les invariants `validate_test_runners_ids` /&nbsp;`validate_test_runners_names` sont appliqués sur `self._tests` (donc post-filter).
- Si la saturation est activée et qu'il ne reste qu'un test, on clone _ce test_ jusqu'à `max_workers`.

## Cas particulier du smoke

L'utilisateur peut décider de _filtrer_ avec `--only` qui s'applique **à toutes les suites**.

- Si aucun test du smoke ne matche `--only`, le smoke a une suite vide&nbsp;→&nbsp;`campaign_has_failed` retourne `False` →&nbsp;main runs, smoke bypassed.
- Si tous les tests du main ne matchent pas non plus, on a juste les `_results` vides.

`--only` est un filtre, pas un sélecteur de hiérarchie. On peut filtrer transversalement par ID.

## Schéma

```
                ┌────────────────────────────────┐
                │ filter_tests_by_ids(tests,     │
                │   only=..., exclude=...)       │
                └──────────────┬─────────────────┘
                               ▼
                ┌────────────────────────────────┐
                │ only_set && exclude_set ?      │── True ─► raise ValueError
                └──────────────┬─────────────────┘
                               ▼
                ┌────────────────────────────────┐
                │ only_set non vide ?            │── True ─► log matched IDs
                └──────────────┬─────────────────┘            return [test for test in tests if test.test_id in only_set]
                               ▼
                ┌────────────────────────────────┐
                │ exclude_set non vide ?         │── True ─► log matched IDs
                └──────────────┬─────────────────┘            return [test for test in tests if test.test_id not in exclude_set]
                               ▼
                          return tests
```
