---
title: "02.11.04 — Loggers : PrintLogger, FileLogger, PrintAndFileLogger, MutedLogger"
description: "Les quatre loggers canoniques d'Ocarina, PrintLogger, FileLogger, PrintAndFileLogger et MutedLogger, plus la factory create_matching_logger, tous opt-in."
weight: 4
date: 2026-05-20
series: ["opinionated"]
series_order: 4
tags: ["ocarina"]
---

# 02.11.04&nbsp;—&nbsp;Loggers&nbsp;: `PrintLogger`, `FileLogger`, `PrintAndFileLogger`, `MutedLogger`

> Dossier source&nbsp;: [`src/ocarina/opinionated/loggers/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/opinionated/loggers)
>
> Quatre implémentations canoniques d'`ILogger`, plus une factory `create_matching_logger`. Toutes opt-in.

## `create_matching_logger`

```python
LOGGERS_CHOICES = ("terminal", "file", "terminal+file", "muted")

def create_matching_logger(mode: SupportedLogger) -> ILogger:
    if mode == "terminal":
        return PrintLogger()
    if mode == "file":
        return FileLogger(base_dir=get_default_log_dir())
    if mode == "terminal+file":
        return PrintAndFileLogger(base_dir=get_default_log_dir())
    if mode == "muted":
        return MutedLogger()
    raise ValueError(f"Unsupported logger mode: {mode}")
```

Et&nbsp;:

```python
def get_default_log_dir() -> Path:
    return Path.cwd() / ".ocarina_logs"
```

→ Par défaut, les logs vont dans `.ocarina_logs/` à la racine du projet utilisateur. Gitignored par convention.

## `PrintLogger`

```python
class PrintLogger(ILogger):
    def __init__(self) -> None:
        self._prefix_thunk: Thunk[str] = lambda: ""
        self._domain_taxonomy: tuple[str, ...] = ("",)

    def set_prefix(self, prefix_thunk: Thunk[str]) -> Self:
        self._prefix_thunk = prefix_thunk
        return self

    def set_domain_taxonomy(self, taxonomy: tuple[str, ...]) -> Self:
        self._domain_taxonomy = taxonomy
        return self

    def raw(self, *args, stream=None, **kwargs) -> None:
        if stream is None:
            stream = sys.stdout
        print(*args, file=stream, **kwargs)

    def info(self, msg, *args, exc=None, **kwargs):
        self._print_log("[INFO]", msg, *args, exc=exc, stream=sys.stdout)
    # ... id. pour critical / error / warning / debug / success / test_name ...
```

- **State**&nbsp;: `_prefix_thunk` (Thunk) + `_domain_taxonomy` (tuple).
- **Sortie**&nbsp;: `sys.stdout` (info, debug, success, test_name) ou `sys.stderr` (critical, error, warning, exception).
- **Format**&nbsp;: `<prefix> [LEVEL] <message>` typiquement, avec ANSI colors si terminal.
- **`cleanup()`**&nbsp;: no-op.

## `FileLogger`

```python
@final
class FileLogger(PrintLogger):
    def __init__(
        self, *,
        base_dir: Path,
        with_flush_effect: bool = True,
        with_fallback_on_print_logger_when_no_taxonomy_effect: bool = True,
    ) -> None:
        self._base_dir = base_dir
        self._with_flush_effect = with_flush_effect
        self._with_fallback_on_print_logger_when_no_taxonomy_effect = (
            with_fallback_on_print_logger_when_no_taxonomy_effect
        )
        super().__init__()

    @property
    def _log_file_path(self) -> Path:
        if len(self._domain_taxonomy) == 1:
            folder_path = self._base_dir
            file_name = f"{self._domain_taxonomy[0]}.log"
        else:
            folder_path = self._base_dir.joinpath(*self._domain_taxonomy[:-1])
            file_name = f"{self._domain_taxonomy[-1]}.log"
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path / file_name
```

| Taxonomy                                               | Folder                           | File                                        |
| ------------------------------------------------------ | -------------------------------- | ------------------------------------------- |
| `("")`                                                 | &nbsp;—&nbsp;                    | &nbsp;→&nbsp;Fallback PrintLogger si activé |
| `("annoncements",)`                                    | `base_dir`                       | `annoncements.log`                          |
| `("e2e", "Login")`                                     | `base_dir/e2e`                   | `Login.log`                                 |
| `("e2e", "Login", "happy paths", "Login without OTP")` | `base_dir/e2e/Login/happy paths` | `Login without OTP.log`                     |

La **taxonomie devient l'arborescence**. Les rapports DOCX (cf. [`05-plugins-reports.md`](05-plugins-reports.md)) parcourent cet arbre récursivement et fabriquent un `.docx` par cas de test.

## `PrintAndFileLogger`

```python
class PrintAndFileLogger(FileLogger):
    # … hérite de FileLogger mais imprime AUSSI dans stdout/stderr …
```

C'est la combinaison par défaut (`create_matching_logger("terminal+file")`). Logs visibles _en CLI_ pour la lecture humaine pendant l'exécution, _et_ écrits sur disque pour les rapports.

## `MutedLogger`

```python
class MutedLogger(ILogger):
    def set_prefix(self, prefix_thunk): return self
    def set_domain_taxonomy(self, taxonomy): return self
    def raw(self, *args, stream=None, **kwargs): pass
    def info(self, msg, *args, exc=None, **kwargs): pass
    # … etc, tout est pass …
    def cleanup(self): pass
```

- Tests internes du framework (on ne veut pas polluer la sortie).
- `match_page` sans logger explicite (`_logger = MutedLogger() if logger is None else logger`).
- Benchmarks où le logging fausserait la mesure.

## `set_prefix`, `Thunk`, `format_metadata_str`

```python
# src/ocarina/opinionated/loggers/utils/format_metadata_str.py
def _format_metadata_str(*, namespace: str, metadata: str) -> str:
    return "[" + namespace + "::" + metadata + "]"


def format_utc_date_metadata_str() -> str:
    return _format_metadata_str(
        namespace="UTC_DATE",
        metadata=datetime.now(UTC).isoformat(),
    )


def format_current_thread_metadata_str() -> str:
    return _format_metadata_str(namespace="THREAD", metadata=current_thread().name)


def concat_metadata(*formatters: Thunk[str]) -> str:
    ...
```

```
[UTC_DATE::2026-05-18T09:42:31.123456+00:00]
[THREAD::ThreadPoolExecutor-0_2]
```

Le `[UTC_DATE::...]` est **consommé en aval** par `generate_docx_proof`&nbsp;:

```python
_DEFAULT_UTC_DATE_REGEX = re.compile(r"\[UTC_DATE::([^]]+)]")

def _replace_utc_date(line: str, *, utc_date_regex: re.Pattern[str]) -> str:
    def _repl(m: re.Match[str]) -> str:
        return (
            datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
            .astimezone()
            .strftime("[%m/%d/%Y | %Hh%M:%S.%f]")
        )
    return utc_date_regex.sub(_repl, line)
```

Le DOCX **traduit** chaque `[UTC_DATE::...]` en date locale formatée. C'est un contrat de format entre le logger et le plugin DOCX.

`set_prefix`&nbsp;:

```python
exceptions_logger = PrintLogger()
    .set_prefix(
        lambda: concat_metadata(
            format_utc_date_metadata_str,
            format_current_thread_metadata_str,
        )
    )
    .set_domain_taxonomy(("Post-execution plugins",))
```

Chaque log a son préfixe `[UTC_DATE::...][THREAD::...]`, recalculé _paresseusement_ à chaque appel.

## `cleanup()`

```python
def cleanup(self) -> None:
    # Flush effect (optionally print to stdout)
    # Close file handle
    # Recycle for next attempt
    ...
```

Appelé par `TestFlow.run` avant un retry (cf. [`../05-orchestration/03-test-flow-retries.md`](../05-orchestration/03-test-flow-retries.md)). Nouveau fichier fichier _frais_ (même path, mais réécrit).

## `with_flush_effect`

Si `True` (default)&nbsp;: à `cleanup()`, le contenu du fichier est **aussi** imprimé en stdout. Utile pour voir _ce qui s'est passé_ dans la tentative qui vient d'échouer (avant de la jeter pour repartir sur une nouvelle).

Si `False`&nbsp;: silent, juste close + recycle.

## Fallback sur PrintLogger lorsque la taxonomie est vide

Si `with_fallback_on_print_logger_when_no_taxonomy_effect` vaut `True` (default)&nbsp;: un `FileLogger` _sans_ taxonomy explicite (c'est-à-dire `("")` ou rien) **fallback en PrintLogger**. Évite d'écrire dans un fichier `.log` à la racine de `base_dir` quand un appelant a oublié de scoper.
