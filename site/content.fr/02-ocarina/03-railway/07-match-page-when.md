---
title: "02.03.07 — match_page / when"
weight: 7
date: 2026-05-20
series: ["railway"]
series_order: 7
tags: ["ocarina"]
---

# 02.03.07&nbsp;—&nbsp;`match_page` /&nbsp;`when`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing_with_railway/match_page.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/match_page.py)
>
> Ajouté **après coup** au framework. Le Holy Book précise&nbsp;: «&nbsp;_`match_page` et `when` ont été ajoutés après coup, l'Igoristan était tellement aléatoire que le cas d'usage s'est imposé de lui-même. Leur implémentation a été simple, preuve de la flexibilité de la grammaire&nbsp;: d'autres structures analogues pourraient très bien suivre._&nbsp;»

## Le problème

Certaines pages d'une application peuvent être rendues différemment&nbsp;:

- Bannière de cookies présente ou non.
- A/B test renvoyant deux variantes d'UI.
- Mode dégradé (page de maintenance) au lieu de la page normale.
- Captcha anti-bot.
- ...

Le scénario doit pouvoir **se brancher** sans casser la chaîne ROP.

## API utilisateur

```python
match_page(
    branches=[
        when(check_that_page.has_cookies_banner,
             name="Has cookies banner",
             then=[drive_page(act(on_homepage, confirm_cookie_banner)
                              .failure(...)
                              .success(...))]),
        when(check_that_page.has_not_cookies_banner,
             name="Has NOT cookies banner",
             then=[]),
    ],
)
```

- **`when(condition, then=..., name=...)`**&nbsp;: déclare une branche.
- **`condition`** est un `Thunk[bool]` (une fonction sans argument qui renvoie `True`/`False`). Évaluée _au runtime_.
- **`then`** est une `TestChain` (i.e. une liste de `ChainRunner`).
- **`name`** est utilisé pour le logging.

> Bonne pratique&nbsp;: ne **pas** utiliser une lambda `not has_X()`. On déclare deux _matchers_ séparés (`has_cookies_banner` /&nbsp;`has_not_cookies_banner`) pour optimiser les délais&nbsp;: ce sont deux cas distincts, avec potentiellement deux timeouts différents.

## Code&nbsp;: `When`

```python
@final
@dataclass(frozen=True)
class When:
    condition: Thunk[bool]
    then: TestChain
    name: str = ""

when = When        # alias d'appel
```

Le `when = When` est une astuce élégante&nbsp;: le _constructeur de dataclass_ devient une «&nbsp;_fonction_&nbsp;» qu'on peut appeler en `when(cond, then=[...], name="...")`, c'est `When(...)`, mais c'est aussi `when(...)`.

## Politique d'exceptions

> - Exceptions listed in `raise_exceptions` are re-raised immediately.
> - All other exceptions raised by `branch.condition()` are interpreted as a non-matching condition (False).

Mécanique&nbsp;: si `condition()` lève une `WebDriverException` (par exemple parce que la page est gelée), on _peut_ vouloir&nbsp;:

- L'interpréter comme «&nbsp;_cette branche ne matche pas_&nbsp;»&nbsp;→&nbsp;on essaie la suivante (politique permissive).
- La faire remonter pour que le rejeu prenne le relais (politique stricte).

Le choix le plus rationnel est de passer `raise_exception=transient_errors` à `create_match_page`.

## Code&nbsp;: `_match_page_builder`

```python
def _match_page_builder(*, raised_exceptions: tuple[type[BaseException], ...] = ()):

    def _match_page(logger: ILogger, branches: Sequence[When]) -> ChainRunner[Any]:

        def _thunk() -> ActionChain[Any]:
            for index, branch in enumerate(branches):
                label = branch.name or f"branch[{index}]"
                try:
                    matched = branch.condition()
                    logger.debug(f"match_page: '{label}' -> {matched}")
                except raised_exceptions as exc:
                    logger.exception("match_page: raising exception...", exc=exc)
                    raise
                except Exception as exc:
                    logger.exception(f"match_page: '{label}' raised", exc=exc)
                    matched = False

                if matched:
                    logger.info(f"match_page: '{label}' matched.")
                    return _run_branch(branch.then)

            return ActionChain(
                has_failed=True,
                result=Fail(error=NoMatchingBranchError(
                    f"No when() branch matched out of {len(branches)} candidate(s)."
                )),
            )

        return ChainRunner(thunk=_thunk)

    return _match_page
```

1. **Évaluation séquentielle, first-match wins**&nbsp;: la première branche `True` est exécutée, les autres sont ignorées.
2. **Logging à trois niveaux**&nbsp;: `debug` pour le check, `info` pour le match, `exception` pour le raise.
3. **Le `try/except` est ordonné**&nbsp;: on attrape d'abord les exceptions explicitement re-raised. Python évalue les `except` dans l'ordre.
4. **Pas de match&nbsp;→&nbsp;`Fail(NoMatchingBranchError(...))`**. Le scénario passe sur le rail d'échec. C'est cohérent avec la grammaire ROP.

## `_run_branch`

```python
def _run_branch(runners: TestChain) -> ActionChain[Any]:
    last: ActionChain[Any] | None = None
    for runner in runners:
        chain = runner.run()
        last = chain
        if chain.has_failed():
            return chain
    if last is None:
        return ActionChain(has_failed=False, result=Ok(value=None))
    return last
```

1. Si **aucun runner**&nbsp;: on retourne `Ok(None)` (branche vide&nbsp;→&nbsp;succès trivial).
2. Si un runner **fail**&nbsp;: court-circuit immédiat, on retourne la chain.
3. Sinon&nbsp;: on retourne le dernier `ActionChain` (succès).

## `create_match_page`

```python
def create_match_page(*, raised_exceptions: tuple[type[Exception], ...] = ()):
    def _match_page(*, logger: ILogger | None = None, branches: Sequence[When]):
        _logger = MutedLogger() if logger is None else logger
        return _match_page_builder(raised_exceptions=raised_exceptions)(
            logger=_logger, branches=branches,
        )
    return _match_page
```

Pattern&nbsp;: **factory de factory (_woop woop!_)**. Le projet utilisateur appelle `create_match_page(raised_exceptions=transient_errors)` une seule fois et stocke le résultat (`match_page`). Toutes les utilisations dans les scénarios partagent la même politique d'exceptions.

Détail&nbsp;: si `logger` n'est pas fourni, on utilise un `MutedLogger`. **Null Object Pattern**, pas de bruit dans la sortie.

## Convention

```python
# lib/ext/ocarina/adapters/agnostic/match_page.py
from ocarina.dsl.testing_with_railway.match_page import create_match_page
from constants.sys.transient_errors import transient_errors

match_page = create_match_page(raised_exceptions=transient_errors)
```

→ Toute exception «&nbsp;_transitoire_&nbsp;» (page d'erreur HTTP, page de vérification absente, etc.) **remonte** plutôt que d'être avalée comme «&nbsp;_non match_&nbsp;». Sans ce câblage, un test qui devrait se rejouer ne se rejouerait pas.

## Schéma d'exécution complet

```
match_page(branches=[
    when(cond_A, name="a", then=[runner_A1, runner_A2]),
    when(cond_B, name="b", then=[runner_B1]),
])

▼

ChainRunner(thunk=_thunk)
  └─ .run()
        │
        ▼
   for branch in branches :
       ┌─ try : matched = branch.condition()
       │      log.debug(f"match_page: 'a' -> True/False")
       ├─ except raised_exceptions : log + RE-RAISE  (transient_error → test rejoué)
       ├─ except Exception         : log + matched = False
       │
       └─ if matched :
              log.info(f"match_page: 'a' matched.")
              return _run_branch(branch.then)
                          │
                          ▼
                 for runner in then :
                     chain = runner.run()
                     if chain.has_failed() : return chain (court-circuit)
                 return last_chain or Ok(None)

   (aucune branche matched)
   return ActionChain(has_failed=True,
                      result=Fail(NoMatchingBranchError(...)))
```

## La spec du Holy Book

Extrait de la page _Premiers scénarios_&nbsp;:

> `match_page` se pose au même niveau que `drive_page` et est chaînable. Sa commande `then` attend à nouveau une chaîne de `drive_page` ou `match_page`. Les branches sont définies par `when`.

Et&nbsp;:

> `match_page` et `when` ont été ajoutés après coup, l'Igoristan était tellement aléatoire que le cas d'usage s'est imposé de lui-même. Leur implémentation a été simple, preuve de la flexibilité de la grammaire&nbsp;: d'autres structures analogues pourraient très bien suivre.

La preuve de la flexibilité est importante&nbsp;: c'est l'argument méta du framework. Le DSL est extensible par composition («&nbsp;_retourner un `ChainRunner`_&nbsp;») sans toucher au framework. Voir [`../../11-independence/01-sovereign-grammar.md`](../../11-independence/01-sovereign-grammar.md)

## Recommandations issues du Holy Book

> Un _matcher_ vérifie de manière minimale si quelque chose est vrai, en allant au plus vite.

Et&nbsp;:

> ⚠️ Il vaut mieux éviter un `.find_element(s)` brut&nbsp;: c'est la voie rapide vers la _flakiness_.
>
> Le délai maximal de 5 secondes n'aura aucun impact dans une batterie scalée horizontalement, ce n'est donc pas une pratique à craindre ici. Il n'est pas non plus recommandé de déguiser un `verify` en _matcher_&nbsp;: **ce sont deux outils différents.**

| Outil                             | But                                  | Timeout typique         |
| --------------------------------- | ------------------------------------ | ----------------------- |
| `verify(...)`                     | Garantir qu'on est sur la bonne page | global `--wait-timeout` |
| matcher (`has_cookies_banner`, …) | Identifier la bonne branche          | court (1-5 s)           |
