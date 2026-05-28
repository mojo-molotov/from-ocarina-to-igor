---
title: "04.06 — Property-based testing (hypothesis)"
description: "Le property-based testing d'Ocarina avec hypothesis : génération d'inputs et vérification de propriétés universelles sur les prédicats d'invariants."
weight: 6
date: 2026-05-20
series: ["tests-internes"]
series_order: 6
tags: ["invariants"]
---

# 04.06&nbsp;—&nbsp;Property-based testing (`hypothesis`)

> Un seul fichier (`test_invariants_properties.py`), mais le pattern est intéressant&nbsp;: on **génère** des inputs et on vérifie des **propriétés universelles** des prédicats d'invariants.

## Le concept

`hypothesis` génère automatiquement des _cas de test_ qui satisfont des contraintes données, puis vérifie qu'une propriété est vraie pour tous les cas générés. En cas d'échec, _hypothesis_ fait du **shrinking** pour trouver le **plus petit contre-exemple**.

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_is_positive_passes_on_positive(value):
    if value >= 0:
        is_positive(value)             # ne doit pas lever
    else:
        with pytest.raises(InvariantViolationError):
            is_positive(value)         # doit lever
```

→ `hypothesis` génère des entiers (typiquement 100 par défaut), vérifie la propriété pour chacun. Si une exception _inattendue_ surgit, c'est un fail. Le shrinker trouve le plus petit cas qui fail (`0`&nbsp;? `-1`&nbsp;? `MIN_INT`&nbsp;?).

## Propriétés testées dans Ocarina

Le fichier `test_invariants_properties.py` couvre plusieurs prédicats&nbsp;:

| Prédicat                     | Propriété testée                                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| `is_positive(v)`             | passe si et seulement si `v >= 0`                                                                         |
| `is_not_zero(v)`             | passe si et seulement si `v != 0`                                                                         |
| `is_in(elements)(v)`         | passe si et seulement si `v in elements`                                                                  |
| `has_unique_elements()(seq)` | passe si et seulement si `len(seq) == len(set(seq))`                                                      |
| `is_iso_date_string(s)`      | passe si et seulement si `datetime.fromisoformat(s)` ne lève pas                                          |
| `is_email(s)`                | passe si et seulement si `s` matche les contraintes définies (1 `@`, parts non vides, `.` dans le domain) |

## Pourquoi `hypothesis` plutôt que des tests explicites

| Tests explicites                                          | Hypothesis                                             |
| --------------------------------------------------------- | ------------------------------------------------------ |
| Couvre les cas auxquels on a pensé                        | Couvre les cas auxquels on n'a _pas_ pensé             |
| Si on rate un edge case, le test passe                    | Si un edge case existe, _hypothesis_ tend à le trouver |
| Maintenance&nbsp;: ajouter un edge case = ajouter un test | Maintenance&nbsp;: la propriété est stable             |
| Documente _ce qui marche_                                 | Documente _la propriété mathématique_                  |

## Hypothesis Statistics

```
=== Hypothesis Statistics ===

test_is_positive_passes_on_positive:
    - 100 passing examples, 0 failing examples, 0 invalid examples
    - Typical runtimes: 0-1 ms, ~ 50% in 0.0 ms
    - Shrinking events: 0
```

Permet de voir combien d'exemples ont été générés, le temps moyen, et si le shrinker a été invoqué.

## Échec

Imaginons que `is_positive` ait un bug&nbsp;: il accepte `-1` par erreur.

```
Falsifying example: test_is_positive_rejects_negative(value=-1)
```

`hypothesis` indique l'input exact qui fail. Pas besoin de chercher.

## Limites

`hypothesis` ne remplace **pas** les tests fonctionnels&nbsp;; il les complète.

Il est très utile pour&nbsp;:

- Les fonctions «&nbsp;_pures_&nbsp;» (un input, un output déterministe).
- Les invariants («&nbsp;_cette propriété est vraie pour tout `x`_&nbsp;»).

C'est pour ça qu'il est concentré sur `test_invariants_properties.py`

## `--hypothesis-show-statistics`

```makefile
-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

→ À la fin du run, on voit les stats de toutes les invocations `@given(...)`.

Permet de détecter&nbsp;:

- Trop d'_invalid examples_ (la stratégie génère mal).
- Temps moyens anormaux (le test est lent).
- Shrinking trop fréquent (test instable, propriété mal formulée).

## Fuzzing

`hypothesis` peut aussi faire du _stateful testing_ (`RuleBasedStateMachine`) qui génère des séquences d'actions sur un état mutable. Ce mécanisme n'est **pas utilisé** dans Ocarina.

- Les classes principales (`Test`, `TestSuite`) sont _immutables_ ou stateful de façon strictement contrôlée.
- Le DSL est déclaratif.
