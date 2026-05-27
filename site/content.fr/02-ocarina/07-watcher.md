---
title: "02.07 — Watcher[Driver]"
weight: 7
date: 2026-05-20
series: ["ocarina"]
series_order: 7
tags: ["watcher", "selenium"]
---

# 02.07&nbsp;—&nbsp;`Watcher[Driver]`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/watcher.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/watcher.py)
>
> Observateur parallélisé qui tourne en _daemon thread_ aux côtés de la `test_chain`. Conçu pour détecter les **frictions imprévisibles et sans impact direct sur le scénario** qui se produisent _pendant_ que le scénario tourne&nbsp;: toasts d'erreur aléatoires, validations parasites, popups inattendus.

## Le problème

Citation du Holy Book (_handling-flakiness_)&nbsp;:

> Plus surprenant encore&nbsp;: des applications affichant des toasts d'erreur sans raison apparente, ou des formulaires signalant des erreurs de validation sur des saisies pourtant correctes, sans pour autant bloquer le parcours.
>
> Ces erreurs sont les plus pénibles à détecter, car elles sont _indolores_. On ne peut pas simplement constater un crash et ajouter une _politique de retry_ en attendant que l'anomalie soit corrigée. Elles sont, pour ainsi dire, invisibles.
>
> Il resterait à massacrer les scénarios de test ou à recourir à des «&nbsp;_techniques de ninjas_&nbsp;». Ocarina refuse ces deux options.
>
> La solution, les _watchers_.

## Code

```python
@final
class Watcher[Driver]:
    def __init__(
        self,
        *,
        callback: Callable[[Watcher[Driver]], None],
        name: str,
        poll_interval: float | None = None,
    ) -> None:
        self._callback = callback
        self._poll_interval = (
            poll_interval if poll_interval is not None and poll_interval > 0.1 else 0.5
        )
        self._stop_event: threading.Event | None = None
        self._cache: set[str] = set()
        self._thread: threading.Thread | None = None
        self._logger: ILogger | None = None
        self._take_screenshot: ITakeScreenshot[Driver] | None = None
        self._driver: Driver | None = None
        self.name = name
```

| Paramètre       | Type                                | Rôle                                                                | Default       |
| --------------- | ----------------------------------- | ------------------------------------------------------------------- | ------------- |
| `callback`      | `Callable[[Watcher[Driver]], None]` | Fonction appelée à chaque poll cycle. Reçoit le `Watcher` lui-même. | &nbsp;—&nbsp; |
| `name`          | `str`                               | Nom du watcher (pour scoping du logger)                             | &nbsp;—&nbsp; |
| `poll_interval` | `float \| None`                     | Délai entre 2 appels callback. Min 0.1s.                            | 0.5           |

## Cycle de vie

```
1. Watcher(callback=..., name="cookies", poll_interval=0.8)    # construction, inert

2. watcher.start(driver, logger, take_screenshot)
       │
       ├─ stop_event = Event()                       # nouveau event par start
       ├─ self._stop_event = stop_event              # mémorisé
       ├─ self._thread = Thread(target=_loop,
       │                        args=(stop_event,),
       │                        daemon=True)         # daemon : ne bloque pas le shutdown
       └─ thread.start()

3. test_chain s'exécute en parallèle, le thread tourne :
       │
       └─ _loop(stop_event) :
            while not stop_event.is_set() :
                with suppress(Exception) :
                    self._callback(self)
                stop_event.wait(self._poll_interval)

4. watcher.stop()
       │
       ├─ self._stop_event.set()                     # signal d'arrêt
       └─ self._thread.join(timeout=poll_interval * 2)
```

## `start()`

```python
def start(self, driver, logger, take_screenshot) -> None:
    # Defensively terminate any thread leaked from a previous start()
    # whose stop()/join() timed out. Its loop holds the previous Event
    # in its local frame ; setting it here guarantees the leaked thread
    # exits at the end of its current callback iteration instead of
    # racing with the new thread on shared self._driver / self._logger.
    if self._stop_event is not None:
        self._stop_event.set()

    self._driver = driver
    self._logger = logger
    self._take_screenshot = take_screenshot
    stop_event = threading.Event()
    self._stop_event = stop_event
    self._thread = threading.Thread(
        target=self._loop, args=(stop_event,), daemon=True
    )
    self._thread.start()
```

### 1. Le `stop_event` est passé _par argument_ au thread, pas via `self`

```python
self._thread = threading.Thread(target=self._loop, args=(stop_event,), daemon=True)
```

Si un `start()` _précédent_ a leaké un thread (à cause d'un `join` timeout), ce thread garde son propre `stop_event`. Si l'on stockait l'event seulement dans `self._stop_event`, le nouveau `start()` réécrirait `self._stop_event`, mais l'ancien thread continuerait avec son _ancien_ event.

`set()` l'ancien `self._stop_event` _avant_ de le remplacer. Chaque thread accède à son event via son argument de fonction. L'ancien thread voit son event `set()`&nbsp;→&nbsp;il sort proprement à la fin du prochain poll.

### 2. `daemon=True`

Le thread est _daemon_. Si le process Python se termine, le thread est tué automatiquement. Pas de blocage du shutdown.

### 3. Injection runtime

`driver`, `logger`, `take_screenshot` ne sont **pas** passés au constructeur du watcher. Ils sont injectés par `start()`, donc _par tentative_ (chaque tentative a son driver propre). Cohérent avec le cycle de vie d'un test.

## `_loop`

```python
def _loop(self, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        with suppress(Exception):
            self._callback(self)
        stop_event.wait(self._poll_interval)
```

1. **`with suppress(Exception)`**&nbsp;: la callback peut lever **n'importe quoi**, c'est attrapé silencieusement. _Un watcher ne doit jamais crasher un test._
2. **`stop_event.wait(poll_interval)`**&nbsp;: équivalent à `time.sleep(poll_interval)`, mais réveillé immédiatement si `stop_event.set()` est appelé. Évite d'attendre 0.8s à la fin pour rendre la main.

## API `driver`, `cache`, `report`

```python
@property
def driver(self) -> Driver:
    if self._driver is None:
        raise RuntimeError("Watcher.driver accessed before start() was called.")
    return self._driver

@property
def cache(self) -> set[str]:
    return self._cache

def report(self, message: str, *, label: str = "WATCHER") -> None:
    if (self._driver is None or self._logger is None or self._take_screenshot is None):
        return
    with suppress(Exception):
        self._logger.info(message)
        self._take_screenshot(self._driver, self._logger, label)
```

| Élément                            | Description                                                                         |
| ---------------------------------- | ----------------------------------------------------------------------------------- |
| `driver` (property)                | Le `WebDriver` injecté au `start()`. Lève `RuntimeError` si accédé avant `start()`. |
| `cache` (property)                 | Un `set[str]` mutable pour la déduplication des reports.                            |
| `report(message, label="WATCHER")` | Émet un log info + prend un screenshot.                                             |

## Pattern de déduplication

```python
def catch_me_if_you_can_cb(watcher: SeleniumWatcher) -> None:
    elements = watcher.driver.execute_script(
        "return Array.from(document.querySelectorAll('.catch-me-if-you-can'));"
    )
    if not elements:
        return

    for attrs in extract_attrs(elements):
        fingerprint = ":".join(filter(None, [
            attrs["tag"], attrs["text"], attrs["id"], attrs["cls"],
            attrs["name"], attrs["testid"],
        ]))
        if fingerprint in watcher.cache:
            continue
        watcher.cache.add(fingerprint)
        watcher.report(
            f"catch-me-if-you-can element detected: <{attrs['tag']}> {attrs['text']!r}",
            label="CATCH_ME_IF_YOU_CAN",
        )
```

Voir [`../07-ocarina-example/09-watcher-catch-me.md`](../07-ocarina-example/09-watcher-catch-me.md) pour le détail.

## Pourquoi du JS dans la callback

Le Holy Book le justifie&nbsp;:

> Le _watcher_ est tolérant aux erreurs&nbsp;: il les avale silencieusement. Il n'y a donc aucun intérêt à utiliser une fonction Selenium pour capturer un élément de la page, si ce n'est s'encombrer. Utiliser les fonctions natives de Selenium imposerait de gérer des questions d'_implicit timeout_.
>
> Passer directement par du _Javascript_ permet de contourner toute logique de _polling_ interne et de rendre l'exécution du _watcher_ la moins bloquante possible pour le test qui tourne sur le même _driver_.
>
> Ce tour de passe-passe devient alors invisible, puisqu'il n'est que d'une durée de quelques millisecondes.

Donc&nbsp;: `driver.execute_script("...")` plutôt que `driver.find_element(...)`. Pas d'implicit wait, pas de polling Selenium, JS direct.

## Convention «&nbsp;_négatifs uniquement_&nbsp;» (côté projet IA)

Le `CLAUDE.md` de `ocarina-with-ai-example` formalise&nbsp;:

> **Les signaux des watchers sont négatifs uniquement.** Un watcher qui émet «&nbsp;_login réussi_&nbsp;» casse le contrat.

Sens&nbsp;: un watcher détecte des **frictions** qu'on ne voulait pas voir. Pas des succès. Le succès est l'affaire du `test_chain` (avec `log_success`), pas des watchers.

## `create_selenium_watcher`

```python
# src/ocarina/dsl/testing/selenium/create_watcher.py
type SeleniumWatcher = Watcher[WebDriver]

def create_selenium_watcher(
    *,
    callback: Callable[[SeleniumWatcher], None],
    name: str,
    poll_interval: float | None = None,
):
    return Watcher(callback=callback, name=name, poll_interval=poll_interval)
```

Comme `create_selenium_test`, c'est un alias typé sur Selenium.

## Taxonomie des loggers de watchers

Quand `TestExecutor._start_watchers` est appelé&nbsp;:

```python
watcher_name = (
    f"[{index + 1}] {test_name} - {watcher.name}"
    if len(watchers) > 1
    else f"{test_name} - {watcher.name}"
)
watcher_taxonomy = (*taxonomy[:-1], watcher_name)
scoped_logger = self._create_logger().set_domain_taxonomy(watcher_taxonomy)
watcher.start(driver, scoped_logger, self._take_screenshot)
```

Conséquence sur le `FileLogger`&nbsp;:

```
.ocarina_logs/
  e2e/
    Randomness/
      Chaotic form/
        Send the chaotic form.log                          ← log du test
        Send the chaotic form - catch-me-if-you-can.log    ← log du watcher
```

Le rapport DOCX peut alors présenter le log du watcher _à côté_ du log du test, _comme une frise temporelle parallèle_.
