---
title: "02.10.01 — WebDriversPool[Driver]"
description: "WebDriversPool[Driver] : la pool thread-safe d'Ocarina, concurrence garantie par sémaphore, warmup surveillé et driver neuf à chaque acquisition."
weight: 1
date: 2026-05-20
series: ["infra"]
series_order: 1
tags: ["ocarina"]
---

# 02.10.01&nbsp;—&nbsp;`WebDriversPool[Driver]`

> Fichier source&nbsp;: [`src/ocarina/infra/drivers_pool.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/drivers_pool.py)
>
> Pool thread-safe de drivers, max concurrence garantie par sémaphore, _warmup_ asynchrone surveillé, _shutdown_ propre. Pas de réutilisation&nbsp;: chaque `acquire()` détruit son driver à la fin (état propre).

## Constructeur

```python
@final
class WebDriversPool[Driver]:
    def __init__(
        self,
        create_driver: Thunk[BuiltWebDriver[Driver]],
        max_size: int,
        warmup_timeout: float | None = None,
    ) -> None:
        self._create_driver = create_driver
        self._pool: Queue[BuiltWebDriver[Driver]] = Queue(max_size)
        self._semaphore = Semaphore(max_size)
        self._warmup_timeout = (
            warmup_timeout if warmup_timeout is not None and warmup_timeout > 0.1
            else 60.0 * 5
        )
```

| Primitive             | Rôle                                                                                                           |
| --------------------- | -------------------------------------------------------------------------------------------------------------- |
| `Queue(max_size)`     | File des drivers _pré-créés_ disponibles.                                                                      |
| `Semaphore(max_size)` | Garantit que **jamais plus de `max_size` drivers** ne vivent simultanément (qu'ils soient en queue ou acquis). |
| `warmup_timeout`      | Délai max sans progression de warmup avant de lever `WarmupTimeoutError`. Par défaut 300s.                     |

## `acquire()`

```python
@contextmanager
def acquire(self) -> Iterator[Driver]:
    try:
        driver, dispose = self._pool.get_nowait()
    except Empty:
        self._semaphore.acquire()
        try:
            driver, dispose = self._create_driver()
        except Exception:
            self._semaphore.release()
            raise

    try:
        yield driver
    finally:
        with suppress(Exception):
            dispose()
        self._semaphore.release()
```

```
              acquire()
                  │
                  ▼
   ┌──────────────────────────────────┐
   │ pool.get_nowait()                │── OK ─► driver, dispose         ← cas warmup
   └──────────────┬───────────────────┘
                  │ Empty
                  ▼
   ┌──────────────────────────────────┐
   │ sem.acquire()                    │  ← bloque si N drivers vivants
   └──────────────┬───────────────────┘
                  ▼
   ┌──────────────────────────────────┐
   │ create_driver()                  │── leve ─► sem.release(); raise
   └──────────────┬───────────────────┘
                  ▼
   ┌──────────────────────────────────┐
   │ yield driver                     │  ← caller utilise
   └──────────────┬───────────────────┘
                  ▼
                finally :
                  with suppress : dispose()       ← driver détruit
                  sem.release()                   ← rend une place
```

### 1. Pas de réutilisation

`Queue.get_nowait()` _consomme_ l'entrée. Une fois sorti, le driver n'est jamais remis dans la queue. À la fin (`finally`), il est **disposé**.

**Aucun driver ne sert pour 2 tests.**

### 2. Pas de leak de sémaphore

- Si `pool.get_nowait()` retourne un driver&nbsp;: on l'utilise, on dispose, on release. ✅
- Si `pool.get_nowait()` lève `Empty`&nbsp;: on acquire le sem, on crée, on utilise, on dispose, on release. ✅
- Si `create_driver()` lève&nbsp;: on release le sem avant de propager. ✅
- Si `dispose()` lève&nbsp;: on suppress + on release. ✅

Tous les chemins libèrent le sémaphore. Pas de fuite.

### 3. Concurrence garantie ≤ max_size

Le sémaphore est acquis **avant** la création, donc tant que `N` drivers sont vivants (créés ou en queue), le `N+1`e appelant attend.

## `warmup()`

```python
def warmup(self) -> None:
    progress = {"count": 0}
    lock = threading.Lock()
    stop_event = threading.Event()

    def worker() -> None:
        while not self._pool.full() and not stop_event.is_set():
            if not self._semaphore.acquire(blocking=False):
                break
            try:
                driver, dispose = self._create_driver()
                self._pool.put((driver, dispose))
                with lock:
                    progress["count"] += 1
            except Exception:
                self._semaphore.release()
                break

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    start_global = time.monotonic()
    last_progress = 0

    while t.is_alive():
        time.sleep(0.5)
        with lock:
            current = progress["count"]

        if current != last_progress:
            last_progress = current
            start_global = time.monotonic()

        if time.monotonic() - start_global > self._warmup_timeout:
            stop_event.set()
            msg = (
                "Warmup stalled (no progress detected)."
                " Some browser processes may still be running."
                " Please check your system (Activity Monitor / Task Manager / Dock)"
                " and close any remaining browser instances."
            )
            self.shutdown()
            raise WarmupTimeoutError(msg)

    t.join()
```

| Thread                          | Rôle                                                                                                                                                                                       |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Worker** (daemon)             | Crée des drivers en boucle tant que la queue n'est pas pleine et que `stop_event` n'est pas set. À chaque succès, incrémente `progress["count"]`.                                          |
| **Watchdog** (thread principal) | Boucle, échantillonne `progress["count"]` toutes les 0.5s. Si la valeur change, **reset** le timer. Si le timer dépasse `warmup_timeout`, `stop_event.set()` + `raise WarmupTimeoutError`. |

C'est un **watchdog basé sur la progression**, pas sur le temps absolu. Si la création d'un driver prend 30s mais que la progression _avance_, c'est OK. Si la création se bloque indéfiniment, la progression stagne&nbsp;→&nbsp;watchdog lève.

## `shutdown()`

```python
def shutdown(self) -> None:
    while not self._pool.empty():
        _, dispose = self._pool.get_nowait()
        with suppress(Exception):
            dispose()
        self._semaphore.release()
```

- Dispose tous les drivers **dans la queue** (pas ceux _acquis_&nbsp;—&nbsp;ils sont gérés par leur `acquire()` context).
- Release les sémaphores correspondants.
- `suppress(Exception)`&nbsp;: si un `dispose()` lève, on continue avec les suivants.

Appelé&nbsp;:

1. Par `TestSuite.run` en cas de `WarmupTimeoutError`.
2. Via `atexit.register(pool.shutdown)` à la fin du process (cf. `infra/selenium/create_drivers_pool.py`).

## `WarmupTimeoutError`

```python
class WarmupTimeoutError(Exception):
    """Raised when warmup is blocked (mostly some macOS edge cases)."""
```

«&nbsp;_macOS edge cases_&nbsp;»&nbsp;: lorsqu'on désactive le mode headless et que l'on décide de fermer une fenêtre d'un navigateur piloté par Ocarina, macOS ne "tue" pas le process lié à la fenêtre.

Ce cas très spécifique a mis en avant la possibilité d'un _hang_ infini dans le programme, et donc la mise en place d'un watchdog naïf.

## Tests dédiés

[`tests/scenarios/test_drivers_pool.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_drivers_pool.py) couvre&nbsp;:

- acquisition /&nbsp;release standard,
- warmup,
- détection WarmupTimeoutError quand le facteur stalle,
- comportement quand `create_driver` lève (release du sem),
- shutdown.
