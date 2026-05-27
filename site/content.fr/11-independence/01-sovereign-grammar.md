---
title: "11.01 — Grammaire souveraine"
description: "Pas de DSL imposé. Pas d'écosystème de plugins. Extension par composition, jamais par héritage."
weight: 1
date: 2026-05-20
series: ["independance"]
series_order: 1
---

# 11.01&nbsp;—&nbsp;Grammaire souveraine

> Pas de DSL imposé. Pas d'écosystème de plugins. Extension par **composition**, jamais par héritage.

## Vision

Citation du Holy Book (chapitre «&nbsp;_Qu'est donc Ocarina&nbsp;?_&nbsp;»)&nbsp;:

> _Et si déléguer sa grammaire à des "standards" n'avait jamais été une bonne idée&nbsp;?_
>
> Le vrai hiatus du test E2E **n'est pas d'imposer la "meilleure" novlangue**.
> Réponse simple&nbsp;: Ocarina est **extensible**.
>
> On y crée les verbes et conjonctions que l'on veut, le tout régi par des **règles strictes qui poussent l'ensemble à rester profondément cohérent**.
>
> Il reste alors à garantir la **traçabilité et la robustesse**.

## «&nbsp;_Retourner un `ChainRunner`_&nbsp;»

Citation du Holy Book (chapitre «&nbsp;_Extensibilité_&nbsp;»)&nbsp;:

> La grammaire des scénarios de test repose sur un seul type&nbsp;: `ChainRunner[T]`. Un scénario est une `list[ChainRunner]` exécutée séquentiellement, court-circuitée au premier échec. `drive_page` n'est qu'une fine enveloppe autour de `chain_actions`, qui construit un `ChainRunner`. N'importe quelle fonction renvoyant un `ChainRunner` s'insère sans toucher au framework.

→ **Un seul type d'extension**&nbsp;: `ChainRunner[T]`. Tout ce qui en retourne un est composable.

## «&nbsp;match_page ajouté après coup&nbsp;»

Le Holy Book mentionne explicitement que `match_page` est un ajout _post-conception_&nbsp;:

> `match_page` et `when` ont été ajoutés après coup, l'Igoristan était tellement aléatoire que le cas d'usage s'est imposé de lui-même. Leur implémentation a été simple, preuve de la flexibilité de la grammaire&nbsp;: d'autres structures analogues pourraient très bien suivre.

→ La _preuve par l'exemple_&nbsp;: si on a pu ajouter `match_page` sans toucher au DSL existant, on peut ajouter `skip_if`, `repeat_n`, ou n'importe quoi d'autre. Cf. [`../02-ocarina/03-railway/07-match-page-when.md`](../02-ocarina/03-railway/07-match-page-when.md)

## «&nbsp;skip_if&nbsp;»

Citation du Holy Book&nbsp;:

> Autre exemple envisageable&nbsp;: **`skip_if`**, qui court-circuiterait volontairement une portion du scénario sur une condition sans échouer (retournerait un `Ok` neutre), utile pour des étapes optionnelles selon l'environnement ou les données de test.

→ Hypothétique idiome à implémenter soi-même. Implémentation triviale&nbsp;: retourne un `ChainRunner[Any]` qui appelle la condition, et soit exécute la branche, soit retourne `Ok(None)`.

L'utilisateur peut l'écrire dans son projet **dès maintenant**, sans attendre de release de la part d'Ocarina.

## Adapters projet

Le projet utilisateur **n'utilise jamais** les classes Ocarina directement.  
Il les _wrappe_ dans des adapters&nbsp;:

```python
# projet/lib/ext/ocarina/adapters/agnostic/act.py
def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        # ... policy projet ...
    return create_act(pom, action, on_failure=failure_hook)


# projet/lib/ext/ocarina/adapters/selenium/test_suite.py
class TestSuite(OriginalTestSuite[WebDriver]):
    def __init__(self, *, name, tests, drivers_pool, ...):
        super().__init__(
            ...,
            max_retries_per_test=8,                    # ← figé pour le projet
            transient_errors=transient_errors,         # ← scopé projet
            ...
        )
```

→ Chaque projet a **son propre framework** au-dessus du framework.  
C'est la souveraineté grammaticale matérialisée.

## Pas de version-locking forcé

Si le framework évolue (par exemple ajoute un paramètre `max_retries_per_test`), le projet&nbsp;:

- Soit accepte le default (rien à faire).
- Soit met à jour son adapter `TestSuite` pour figer une nouvelle valeur.

Pas de cascade de breaking changes dans tout le projet.

## «&nbsp;_Rétrécir_&nbsp;»

Le Holy Book (chapitre «&nbsp;_Premiers pas_&nbsp;», section `TestSuite` adapter)&nbsp;:

> C'est l'_adapter_ le plus important à comprendre. `TestSuite` expose nativement un grand nombre de paramètres. L'objectif de cet _adapter_ est de créer une **façade**&nbsp;: certaines valeurs sont figées une bonne fois pour toutes (_hard-codées_), d'autres sont exposées optionnellement avec des valeurs par défaut. C'est un _rétrécissement_.

→ L'adapter projet **réduit** la surface API d'Ocarina à _ce dont le projet a besoin_.

## Pas d'écosystème de plugins

Cf. [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)&nbsp;:

> _Robot Framework_, a essayé de la contourner avec un _DSL_ (_Domain Specific Language_), incluant **leur propre format** et **leur propre écosystème de plugins**. Ainsi, RF impose de-facto ses propres standards&nbsp;: c'est le coût immédiat de sa promesse.

Ocarina **refuse** d'avoir un écosystème de plugins.

| Avec écosystème                                                             | Sans                              |
| --------------------------------------------------------------------------- | --------------------------------- |
| Plugin marketplace, versions à suivre                                       | Pas de marketplace, juste du code |
| Risque de plugin breaking au upgrade                                        | Pas de risque                     |
| Standards de fait imposés («&nbsp;_comment écrire un bon plugin RF_&nbsp;») | Liberté de pattern                |
| Dépendances cachées                                                         | Tout est local au projet          |

→ Le «&nbsp;_plugin_&nbsp;» que tu cherches = `pip install <ta lib>`. La grande majeure partie du temps.  
Aucun intérêt de refaire le monde.

## Grammaire **régie par des règles strictes**

Citation&nbsp;:

> régi par des **règles strictes qui poussent l'ensemble à rester profondément cohérent**.

| Règle                                        | En pratique                                         |
| -------------------------------------------- | --------------------------------------------------- |
| `ChainRunner[T]` pour tout point d'extension | Type checking force la cohérence                    |
| `@final` partout dans le DSL                 | Pas d'héritage utilisateur, composition obligatoire |
| `mypy strict = true`                         | Aucune "liberté" de typage faible                   |
| `ruff select = ["ALL"]`                      | Aucune "liberté" de style                           |
| Adapters projet rétrécissants                | Aucune surface API par défaut, juste ce qui sert    |

→ La **liberté grammaticale** vit _au-dessus_ d'une discipline _stricte_. C'est la rigueur qui rend la liberté possible.

## λ-calcul

Cf. [`../01-philosophy/04-citations-and-influences.md`](../01-philosophy/04-citations-and-influences.md)&nbsp;:

> Ce que l'on pensait depuis les années 1930, **depuis l'invention du λ-calcul**, est enfin scalable à l'échelle que l'on aurait toujours voulu lui donner.

Le λ-calcul est l'exemple ultime de grammaire souveraine&nbsp;: cœur extrêmement minimal (`λx.M`), règles strictes (β-réduction, α-conversion, η-conversion), tout le reste se compose. Aucun «&nbsp;_plugin λ_&nbsp;».

Ocarina suit la même posture.

## La cohérence avec l'IA

Une grammaire souveraine et statiquement typée est **lisible par une IA** parce qu'elle est petite et régie par des règles algébriques qui ont du sens. Pas de DSL ad-hoc à parser, pas de _vues de l'esprit_.

C'est ce qui rend `ocarina-with-ai-example` faisable&nbsp;: Claude lit le `CLAUDE.md`, comprend les règles strictes, applique. Il _ne pourrait pas_ aussi bien collaborer sur un projet RF avec plugins exotiques puisqu'il devrait apprendre chaque plugin et passerait à côté de beaucoup de règles «&nbsp;_tacites_&nbsp;».
