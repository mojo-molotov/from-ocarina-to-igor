---
title: "02.09 — Ports : ILogger, ITakeScreenshot"
weight: 9
date: 2026-05-20
series: ["ocarina"]
series_order: 9
---

# 02.09&nbsp;—&nbsp;Ports&nbsp;: `ILogger`, `ITakeScreenshot`

> Dossier source&nbsp;: [`src/ocarina/ports/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/ports)
>
> Deux ports seulement. C'est tout. Le reste (`WebDriversPool`, `Screenshotter`, etc.) vit dans `infra/`, pas dans `ports/`. La distinction est claire&nbsp;: un _port_ est une abstraction au-dessus de laquelle vit le DSL&nbsp;; une _infra_ est l'implémentation des _adapters_.

## `ILogger`

```python
class ILogger(ABC):
    @abstractmethod
    def set_prefix(self, prefix_thunk: Thunk[str]) -> Self: ...

    @abstractmethod
    def set_domain_taxonomy(self, taxonomy: tuple[str, ...]) -> Self: ...

    @abstractmethod
    def raw(self, *args: object, stream: SupportsWrite[str] | None = None, **kwargs: object) -> None: ...

    @abstractmethod
    def critical(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def error(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def warning(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def info(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def debug(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def test_name(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def success(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def exception(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def cleanup(self) -> None: ...
```

| Méthode                                     | Sémantique                                                                                                                               |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `set_prefix(thunk)`                         | Préfixe **paresseux** appliqué à chaque log (pour timestamps, threads…). Retourne `Self` pour chaining.                                  |
| `set_domain_taxonomy(taxonomy)`             | Définit la hiérarchie de domaine (`(cycle, campaign, suite, test)`). Crucial pour le `FileLogger` qui crée une arborescence de fichiers. |
| `raw(*args, stream=None)`                   | Écriture brute, sans format (utilisé par les plugins de rapport).                                                                        |
| `critical / error / warning / info / debug` | Niveaux standards. Chaque méthode accepte `exc=` pour passer une exception et la formatter.                                              |
| `test_name(msg)`                            | Niveau custom&nbsp;: annonce le test en cours (`logger.test_name(test.name)`).                                                           |
| `success(msg)`                              | Niveau custom&nbsp;: assertion réussie (utilisé par les `.success(...)` handlers).                                                       |
| `exception(msg, exc=)`                      | Logue une exception avec traceback complet.                                                                                              |
| `cleanup()`                                 | Fin de vie&nbsp;: flush + close (pour le `FileLogger`). Recycle le fichier de log entre les retries.                                     |

## Trois choses qui ne sont _pas_ dans `ILogger`

- **Pas de `set_level()`**&nbsp;: le niveau est géré par l'implémentation (ex. `MutedLogger` filtre tout).
- **Pas de `add_handler()`**&nbsp;: pas d'API à la `logging.Logger` du stdlib. La composition se fait par instanciation de loggers différents (`PrintAndFileLogger` wrappe les deux).
- **Pas de `child(name)`**&nbsp;: la taxonomy est passée _en bloc_ avec `set_domain_taxonomy`.

## `set_prefix(thunk)`

```python
logger.set_prefix(lambda: f"[{datetime.now().isoformat()}]")
```

Si on passait une `str`, ce serait calculé _au moment du `set_prefix`_, donc figé. Avec un `Thunk`, le préfixe est calculé _à chaque appel de log_. Idéal pour les timestamps.

```python
exceptions_logger = PrintLogger().set_prefix(
    lambda: concat_metadata(
        format_utc_date_metadata_str,
        format_current_thread_metadata_str,
    )
)
```

Le préfixe résultant ressemble à `[UTC_DATE::2026-05-18T09:42:31.123456+00:00][THREAD::ThreadPoolExecutor-0_2]`.

Le `[UTC_DATE::...]` est consommé _en aval_ par le plugin DOCX, qui le remplace par la date locale formatée (`[05/18/2026 | 11h42:31.123456]`). Le format est donc un **contrat** entre le logger et le plugin de génération.

## `set_domain_taxonomy(taxonomy)`

```python
logger.set_domain_taxonomy(("e2e", "Dashboard login", "Login happy paths", "Login - without OTP"))
```

Conséquence côté `FileLogger`&nbsp;: crée `e2e/Dashboard login/Login happy paths/Login - without OTP.log` sous `base_dir`. Cf. [`11-opinionated/04-loggers.md`](11-opinionated/04-loggers.md)

## `ITakeScreenshot[Driver]`

```python
# src/ocarina/ports/itake_screenshot.py
class ITakeScreenshot[Driver](Protocol):
    def __call__(
        self,
        driver: Driver,
        logger: ILogger,
        category: str,
    ) -> None: ...
```

- **Protocol (PEP 544)**&nbsp;: c'est un _structural type_, n'importe quel callable avec la bonne signature est accepté.
- **Generic sur `Driver`**&nbsp;: `ITakeScreenshot[WebDriver]` est `(WebDriver, ILogger, str) -> None`.
- **Pas de retour**&nbsp;: prendre un screenshot est un `Effect` (au sens d'Ocarina) qui peut échouer silencieusement.

```python
def take_screenshot(driver: WebDriver, logger: ILogger, category: str) -> None:
    create_selenium_screenshotter(driver, logger).take_screenshot(prefix=category)
```

→ Cf. [`10-infra/03-screenshotter.md`](10-infra/03-screenshotter.md) pour la mécanique interne.

## Pourquoi ces deux ports et pas d'autres&nbsp;?

Pourquoi pas un `IDriversPool`&nbsp;? Un `ITestExecutor`&nbsp;? Un `IInvariant`&nbsp;?

**Le pattern d'extension d'Ocarina n'est pas l'héritage**, c'est la **composition par adapters typés**. Les classes du DSL (`TestSuite`, `TestExecutor`, `TestFlow`, `WebDriversPool`) sont _concrètes_ et acceptent des _dépendances_ via leur `__init__`&nbsp;; on remplace le comportement en passant d'autres _instances_.

Les seules abstractions _qui méritaient_ d'être des ports sont&nbsp;:

- `ILogger`&nbsp;: parce qu'il y a plusieurs implémentations canoniques (`Print`, `File`, `PrintAndFile`, `Muted`) et l'utilisateur peut écrire la sienne.
- `ITakeScreenshot[Driver]`&nbsp;: parce que c'est appelé _partout_ et qu'on veut pouvoir le mocker /&nbsp;le rerouter (par exemple en CI&nbsp;: screenshot vers S3 plutôt que vers disque local).

Tout le reste est _composé_, pas hérité.

## `cleanup()`

Rappel ([`05-orchestration/03-test-flow-retries.md`](05-orchestration/03-test-flow-retries.md))&nbsp;:

```python
if outcome.should_retry and attempt < max_attempts:
    logger_with_taxonomy.cleanup()           # ◄── ICI
    time.sleep(attempt)
    continue
```

Pour le `FileLogger`, `cleanup()` ferme le fichier en cours et le recycle. La tentative suivante écrit dans un fichier _frais_.

Pour le `PrintLogger`, `cleanup()` est un no-op.

## `cleanup()` _n'est pas_ un context manager `__exit__`

`ILogger` est _partagé_ entre les tentatives&nbsp;: il a la durée de vie du test, pas d'une tentative. Le pattern context manager (`with logger: ...`) ne marcherait pas pour _réinitialiser_ proprement entre les retries.
