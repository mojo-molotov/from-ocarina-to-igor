---
title: "02.10.06 — L'acteur Playwright : un thread propriétaire"
description: "Comment Ocarina réconcilie l'API sync thread-affine de Playwright avec son modèle threadé : un acteur mono-thread, la marshallisation par submit, et un seuil de liveness contre les drivers morts."
weight: 6
date: 2026-06-01
series: ["infra"]
series_order: 6
tags: ["ocarina", "playwright", "concurrence"]
---

# 02.10.06&nbsp;—&nbsp;L'acteur Playwright&nbsp;: un thread propriétaire

> Dossier source&nbsp;: [`src/ocarina/infra/playwright/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/playwright)
>
> L'adapter Playwright reprend la structure de l'adapter Selenium fichier pour fichier (`create_driver`, `create_drivers_pool`, `create_screenshotter`, `driver_healthcheck`, `mixins`), avec **un fichier en plus**&nbsp;: [`driver.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/playwright/driver.py). Ce fichier mérite un chapitre à lui seul. C'est lui qui réconcilie l'API _sync_ de Playwright, intrinsèquement liée à un thread, avec le modèle threadé d'Ocarina (pool, warmup, Watcher).

## Le problème&nbsp;: l'API sync de Playwright est thread-affine

L'API **sync** de Playwright lie chaque objet qu'elle renvoie (`Playwright`, `Browser`, `BrowserContext`, `Page`, `Locator`, …) au thread qui a appelé `sync_playwright().start()`. Sous le capot, c'est un _greenlet_ épinglé à ce thread. Y toucher depuis un autre thread lève&nbsp;:

```
greenlet.error: cannot switch to a different thread
```

Ça entre en collision frontale avec le modèle de threading d'Ocarina, qui repose sur **trois** points de contact concurrents avec un même driver&nbsp;:

```
   ┌──────────────────┐
   │  warmup thread   │  WebDriversPool.warmup() pré-construit les drivers
   │  (1, dédié)      │  dans un thread dédié, puis les pousse dans la Queue.
   └────────┬─────────┘
            │ build → Queue
            ▼
   ┌──────────────────┐
   │  worker threads  │  Les workers acquièrent un driver depuis la Queue
   │  (N, parallèles) │  et déroulent la chaîne de test dessus.
   └────────┬─────────┘
            │ + en parallèle
            ▼
   ┌──────────────────┐
   │  watcher daemon  │  Le Watcher poll à côté de la chaîne, dans son
   │  (1 par test)    │  propre daemon thread, et lit la page.
   └──────────────────┘
```

Un driver est donc **construit dans un thread** (warmup) et **utilisé depuis un autre** (worker), pendant qu'un **troisième** (watcher) l'observe. Avec l'API sync de Playwright telle quelle, c'est trois `greenlet.error` garantis.

## La solution&nbsp;: un acteur épinglé à un seul thread

`PlaywrightDriver` emballe Playwright dans un **acteur** (_Actor model_)&nbsp;: il possède un unique _thread propriétaire_ (_owner thread_). Tous les objets Playwright vivent sur ce thread, et **personne d'autre n'y touche jamais directement**. Chaque interaction est _marshallisée_ vers le thread propriétaire via `submit()`.

```
   warmup / worker / watcher threads          owner thread (1, privé)
   ─────────────────────────────────          ───────────────────────
                                                 ┌─────────────────┐
   driver.submit(fn) ──────┐                     │  Playwright     │
                           │   Queue[(fn,fut)]   │  Browser        │
   driver.submit(fn) ──────┼────────────────────▶│  BrowserContext │
                           │                     │  Page, Locator  │
   driver.submit(fn) ──────┘                     │                 │
            ▲                                     │  fn(page) tourne│
            │         future.result()             │  ICI, et ICI    │
            └─────────────────────────────────────│  seulement      │
                       résultat (données brutes)  └─────────────────┘
```

Le _handle_ (`PlaywrightDriver`) est donc sûr à créer dans un thread et à utiliser depuis un autre&nbsp;: seul le **travail** touche Playwright, et ce travail tourne toujours sur le thread propriétaire. La pool, le warmup et la parallélisation des workers d'Ocarina survivent intacts, sans renoncer à l'API sync.

```python
def submit[T](self, fn: Callable[[Page], T]) -> T:
    if threading.get_ident() == self._owner_ident:
        raise RuntimeError("Re-entrant submit() on the owner thread would deadlock.")
    if self._dead:
        raise DriverDiedError("PlaywrightDriver is dead: a previous call exceeded its timeout.")
    if self._closed:
        raise RuntimeError("PlaywrightDriver has been disposed.")
    future = self._owner.submit(lambda: fn(self._page))
    try:
        return future.result(timeout=self._call_timeout_s)
    except FuturesTimeoutError as exc:
        self._dead = True
        self._closed = True
        raise DriverDiedError(...) from exc
```

## Pourquoi pas `ThreadPoolExecutor(max_workers=1)`

Un `ThreadPoolExecutor(max_workers=1)` ferait _presque_ l'affaire&nbsp;: un seul worker, les soumissions traitées dans l'ordre. Presque. Le problème est à la **sortie du process**.

Les workers d'un `ThreadPoolExecutor` ne sont **pas** des daemons&nbsp;: ils sont _joints_ par un hook `atexit`. Si le worker est coincé sur un _pipe_ Playwright mort (le navigateur a crashé, le transport ne répond plus), il ne revient jamais&nbsp;—&nbsp;et ce `join` à la sortie **fige le process pour toujours**. Sur un run de CI, c'est un job qui ne se termine pas.

Ocarina remplace donc l'executor par un `_OwnerThread` maison&nbsp;: un thread **daemon** unique qui draine une `Queue` de `(callable, Future)`.

```
   _OwnerThread._run()  (daemon)
   ───────────────────────────────────────────────
   while True:
       item = queue.get()          # bloque jusqu'à la prochaine soumission
       if item is None:            # sentinelle de stop
           return
       fn, future = item
       try:    future.set_result(fn())
       except: future.set_exception(...)   # toute erreur renvoyée au caller
```

La différence est dans la **mort**&nbsp;:

| `ThreadPoolExecutor(max_workers=1)`                          | `_OwnerThread` (daemon)                                                       |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| Worker non-daemon, joint à l'`atexit`                        | Daemon&nbsp;: **abandonné** à la sortie du process                           |
| Worker coincé sur un pipe mort&nbsp;→&nbsp;`join` reste bloqué à l'exit | Worker coincé&nbsp;→&nbsp;jamais joint, le process sort quand même           |
| Pas de contrôle sur le `join`                                | On ne joint **jamais** nous-mêmes (un future en cours n'est pas annulable)   |

Le coût assumé&nbsp;: un _leak par mort_. Quand un driver meurt coincé, son thread, l'appel bloqué et sa closure restent référencés jusqu'à la sortie du process. C'est l'arbitrage délibéré contre le fait de figer tout le run. Mieux vaut fuir un thread mort que ne jamais terminer.

## Le contrat de `submit`

Trois règles, toutes vérifiées par le code&nbsp;:

1. **Renvoyer des données brutes.** `fn` doit retourner du plat et _thread-safe_ (`str`, `bool`, `bytes`, `None`)&nbsp;—&nbsp;jamais une `Page`, un `Locator` ou un `ElementHandle` vivants, qui sont liés au thread propriétaire et inutilisables ailleurs. `PlaywrightTitleMixin` montre le pattern&nbsp;: `return self._driver.submit(lambda page: page.title())`.
2. **Pas de ré-entrance.** Un `submit()` (ou `quit()`) appelé _depuis_ le thread propriétaire attendrait un future que ce même thread est censé résoudre&nbsp;: un _deadlock_. Le code le détecte (`threading.get_ident() == self._owner_ident`) et lève un `RuntimeError` explicite plutôt que de figer.
3. **L'appel est borné.** `future.result(timeout=call_timeout)` pose un seuil.

## `call_timeout`&nbsp;: un seuil de liveness, pas une deadline

Le point le plus subtil. `call_timeout` (180&nbsp;s par défaut) n'est **pas** une deadline par opération. C'est un seuil de _liveness_&nbsp;: il ne sert qu'à transformer un _blocage infini_ sur un thread propriétaire mort en un échec **borné** et éventuel.

Il est volontairement **découplé** de `wait_timeout` (qui, lui, borne les auto-waits de Playwright) et réglé **généreusement**, bien au-dessus du plus lent `submit` légitime&nbsp;: un long _humanized fill_, un gros `timeout=` par appel, plusieurs auto-waits dans une seule lambda.

```
   submit(fn)
      │
      ├── le future résout avant call_timeout ──────────▶ retourne le résultat ✓
      │
      └── call_timeout dépassé
              │  l'owner thread est ENCORE coincé sur fn
              ▼
          driver marqué _dead = True, _closed = True
          le future en cours est ABANDONNÉ (non annulable)
              │
              ▼
          raise DriverDiedError  ──▶  le caller skip / retry avec un driver frais
```

Le biais est assumé&nbsp;: **errer large est le bon choix**. Un `call_timeout` trop serré tuerait des appels lents-mais-vivants&nbsp;; trop large, il détecte simplement un driver mort _plus tard_&nbsp;—&nbsp;ce qui reste infiniment préférable à rester bloqué pour toujours. On le baisse pour une récupération plus rapide des drivers morts, on le monte si un seul appel tourne légitimement plus longtemps.

## `is_dead` ≠ `is_closed`

Deux états, deux significations. Le healthcheck et le screenshotter s'en servent pour distinguer une course de teardown bénigne d'un vrai crash.

| Propriété   | Signification                                                                  | Le driver est…           |
| ----------- | ------------------------------------------------------------------------------ | ------------------------ |
| `is_closed` | `quit()` a été appelé&nbsp;: disposition **volontaire**.                       | réutilisable&nbsp;? non, mais sain |
| `is_dead`   | un appel a dépassé `call_timeout`&nbsp;: l'owner thread est **toujours coincé**. | à **remplacer**, pas réutiliser |

Un driver _mort_ est aussi reporté `closed` (toute disposition future doit court-circuiter). Mais l'inverse est faux&nbsp;: un driver volontairement _disposé_ n'est pas mort. Le `driver_healthcheck` exploite exactement ça&nbsp;:

```python
def playwright_driver_healthcheck(driver: PlaywrightDriver) -> None:
    if driver.is_dead:
        raise DriverDiedError(...)        # vraiment mort
    if driver.is_closed:
        return                            # disposé volontairement → course bénigne, on sort
    try:
        driver.submit(lambda page: page.title())   # ping minimaliste
    except DriverDiedError:
        raise
    except Exception as exc:
        raise DriverDiedError from exc
```

Ça désamorce la course classique du teardown&nbsp;: un callback de watcher encore en vol qui tente un screenshot juste après que la pool a disposé le driver.

## Le boot est borné lui aussi

Un driver peut crasher **pendant** son démarrage (lancement raté, profil verrouillé). Le boot est donc marshallisé comme n'importe quel appel, et borné par le même `call_timeout`&nbsp;:

```python
boot = self._owner.submit(lambda: self._boot(...))
try:
    self._page = boot.result(timeout=self._call_timeout_s)
except FuturesTimeoutError as exc:
    raise DriverDiedError("Playwright boot did not complete…") from exc
except PlaywrightError as exc:
    raise DriverDiedError("Playwright boot failed…") from exc
finally:
    if not booted:
        self._dead = True
        self._closed = True
        self._owner.stop()
```

Sur le chemin d'`acquire()` à la demande, rien d'autre n'attraperait un boot infini&nbsp;: il wedgerait le worker avec le permit de la pool en main. Un thread que l'OS refuse même de spawner (épuisement de ressources) est lui aussi traité comme une panne d'infra&nbsp;—&nbsp;`DriverDiedError`, pas un `RuntimeError` brut qui crasherait le run.

## L'acteur s'insère sans rien changer

Comme `PlaywrightDriver` expose `quit()` et `save_screenshot()`, il satisfait **les contrats génériques existants**&nbsp;: la disposition (`dispose: Effect`) du [`DriverBuilder`](02-driver-builder.md) et le protocole `ScreenshotDriver` du [`Screenshotter`](03-screenshotter.md). Rien d'autre dans `infra/` ne sait jamais qu'il parle à Playwright.

```
   DriverBuilder.dispose ──▶ driver.quit()            (teardown marshallisé, borné)
   Screenshotter         ──▶ driver.save_screenshot() (submit → page.screenshot)
   healthcheck           ──▶ driver.submit(page.title)
```

`quit()` est **idempotent** et marshallise son propre teardown (stop tracing, close context, stop Playwright) sur le thread propriétaire, borné par `call_timeout`, puis demande l'arrêt (sans jamais joindre). Appelé depuis le thread propriétaire, il lève&nbsp;—&nbsp;comme `submit`, ce serait un deadlock.

## La pool et le warmup&nbsp;: pourquoi c'est sûr

C'est tout l'intérêt de l'acteur. `create_playwright_drivers_pool` réutilise le `WebDriversPool` **agnostique** sans modification&nbsp;:

```python
drivers_pool = WebDriversPool(
    create_driver=lambda: create_playwright_driver(browser=..., headless=..., ...),
    max_size=max_size,
    warmup_timeout=warmup_timeout,
)
atexit.register(drivers_pool.shutdown)
```

> Chaque driver possède un thread privé, donc le warmup est sûr&nbsp;: un driver créé **dans le thread de warmup** peut être consommé par **n'importe quel worker** parce que tous les appels Playwright sont marshallisés vers le thread propriétaire.

Le thread qui _crée_ le driver n'est jamais le thread qui _exécute_ Playwright. Le warmup peut donc pré-construire à l'avance, les workers piochent dans la Queue, et personne ne déclenche de `greenlet.error`.

## Le Watcher&nbsp;: observer, pas muter

Un `Watcher` poll dans son propre daemon thread. Un watcher Playwright **PEUT** lire la page depuis son callback&nbsp;—&nbsp;via `watcher.driver.submit(...)`, marshallisé comme le reste, donc sûr entre threads. Mais c'est gouverné par une convention, pas par une interdiction&nbsp;:

- **OBSERVER, pas MUTER.** Le watcher tourne en parallèle de la chaîne de test&nbsp;; muter la page (click/fill) depuis un watcher corromprait l'état du test. Ça vaut dans **tous** les frameworks, Selenium inclus. Le _read-only_ est la responsabilité de l'utilisateur.
- **Toujours passer par `submit`**, jamais toucher `page` directement.
- **Renvoyer du plat** depuis la lambda (`str`/`bool`/`bytes`)&nbsp;—&nbsp;jamais un `Locator` ou un `ElementHandle` vivants.
- **Caveat de performance**&nbsp;: chaque lecture du watcher se sérialise sur le thread propriétaire, à côté des `submit` de la chaîne de test. La contention croît avec la fréquence de poll (`poll_interval`). Les watchers Selenium, qui partagent le driver directement, sont plus libres ici.

```python
def watch_banner(watcher: PlaywrightWatcher) -> None:
    text = watcher.driver.submit(
        lambda page: page.inner_text("#cookie-banner")
        if page.locator("#cookie-banner").count()
        else ""
    )
    if text and text not in watcher.cache:
        watcher.cache.add(text)
        watcher.report(f"Cookie banner: {text!r}", label="BANNER")
```

## Contexte persistant, vidéo et trace

Comme Selenium route toujours par un `user-data-dir`, l'acteur ouvre un **contexte persistant** (`launch_persistent_context`) plutôt qu'un `Browser` standalone&nbsp;: le profil survit à la disposition. Les navigateurs sont livrés avec Playwright (`playwright install`)&nbsp;—&nbsp;d'où **l'absence de `--driver-path`** côté CLI.

Deux artefacts optionnels (off par défaut), transmis à chaque driver de la pool&nbsp;:

| Option             | Effet                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------- |
| `record_video_dir` | Enregistre une vidéo de la session (doit être posé à la création du contexte&nbsp;: Playwright ne l'active pas après coup). |
| `trace_dir`        | Capture une trace Playwright (`trace_<id>.zip`, à ouvrir avec `playwright show-trace`).            |

Chaque driver écrit son propre fichier au nom unique, donc les artefacts par-test n'entrent jamais en collision. Les fichiers s'accumulent d'un run à l'autre&nbsp;—&nbsp;rien n'est écrasé ni nettoyé automatiquement.

## En une phrase

L'API sync de Playwright est épinglée à un thread&nbsp;; Ocarina est threadé. L'acteur réconcilie les deux en confinant **tout** Playwright à un thread propriétaire daemon, en marshallisant chaque appel par `submit`, et en bornant cette marshallisation par un seuil de liveness qui transforme un driver mort en `DriverDiedError` au lieu d'un blocage. Le reste de l'infra ne voit qu'un driver ordinaire avec `quit()` et `save_screenshot()`.
