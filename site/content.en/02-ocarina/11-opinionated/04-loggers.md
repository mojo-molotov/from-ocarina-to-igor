---
title: "02.11.04 — Loggers: PrintLogger, FileLogger, PrintAndFileLogger, MutedLogger"
description: "Ocarina's four canonical loggers, PrintLogger, FileLogger, PrintAndFileLogger and MutedLogger, plus the create_matching_logger factory, all opt-in."
weight: 4
date: 2026-05-20
series: ["opinionated"]
series_order: 4
tags: ["ocarina"]
---

# 02.11.04&nbsp;—&nbsp;Loggers: `PrintLogger`, `FileLogger`, `PrintAndFileLogger`, `MutedLogger`

> Source folder: [`src/ocarina/opinionated/loggers/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/opinionated/loggers)
>
> Four canonical `ILogger` implementations + a `create_matching_logger` factory. All opt-in.

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

And:

```python
def get_default_log_dir() -> Path:
    return Path.cwd() / ".ocarina_logs"
```

→ By default, logs land in `.ocarina_logs/` at the user project root. Gitignored by convention.

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
    # ... id. for critical / error / warning / debug / success / test_name ...
```

- **State**: `_prefix_thunk` (Thunk) + `_domain_taxonomy` (tuple).
- **Output**: `sys.stdout` (info, debug, success, test_name) or `sys.stderr` (critical, error, warning, exception).
- **Format**: typically `<prefix> [LEVEL] <message>`, with ANSI colors if terminal.
- **`cleanup()`**: no-op.

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

| Taxonomy                                               | Folder                           | File                                 |
| ------------------------------------------------------ | -------------------------------- | ------------------------------------ |
| `("")`                                                 | &nbsp;—&nbsp;                    | → Fallback to PrintLogger if enabled |
| `("annoncements",)`                                    | `base_dir`                       | `annoncements.log`                   |
| `("e2e", "Login")`                                     | `base_dir/e2e`                   | `Login.log`                          |
| `("e2e", "Login", "happy paths", "Login without OTP")` | `base_dir/e2e/Login/happy paths` | `Login without OTP.log`              |

The **taxonomy is the folder tree**. The DOCX reports (see [`05-plugins-reports.md`](05-plugins-reports.md)) walk it recursively and emit one `.docx` per test case.

## `PrintAndFileLogger`

```python
class PrintAndFileLogger(FileLogger):
    # … inherits from FileLogger but ALSO prints to stdout/stderr …
```

The default combo (`create_matching_logger("terminal+file")`). Logs visible _on the CLI_ for humans during execution, _and_ written to disk for reports.

## `MutedLogger`

```python
class MutedLogger(ILogger):
    def set_prefix(self, prefix_thunk): return self
    def set_domain_taxonomy(self, taxonomy): return self
    def raw(self, *args, stream=None, **kwargs): pass
    def info(self, msg, *args, exc=None, **kwargs): pass
    # … etc, everything is pass …
    def cleanup(self): pass
```

- Framework's own internal tests (don't pollute the output).
- `match_page` with no explicit logger (`_logger = MutedLogger() if logger is None else logger`).
- Benchmarks where logging would skew the measurement.

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

The `[UTC_DATE::...]` is **consumed downstream** by `generate_docx_proof`:

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

The DOCX **rewrites** each `[UTC_DATE::...]` into a formatted local date. A format contract between the logger and the DOCX plugin.

`set_prefix`:

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

Every log gets its `[UTC_DATE::...][THREAD::...]` prefix, recomputed _lazily_ on each call.

## `cleanup()`

```python
def cleanup(self) -> None:
    # Flush effect (optionally print to stdout)
    # Close file handle
    # Recycle for next attempt
    ...
```

Called by `TestFlow.run` before a retry (see [`../05-orchestration/03-test-flow-retries.md`](../05-orchestration/03-test-flow-retries.md)). _Fresh_ file (same path, overwritten).

## `with_flush_effect`

`True` (default) → at `cleanup()`, the file's contents are **also** printed to stdout. Lets you see _what happened_ in the attempt that just died before it gets recycled.

`False` → silent, just close + recycle.

## Fallback to PrintLogger when the taxonomy is empty

`with_fallback_on_print_logger_when_no_taxonomy_effect=True` (default) → a `FileLogger` _without_ an explicit taxonomy (`("")` or nothing) **falls back to PrintLogger**. Stops you from writing a `.log` at the root of `base_dir` when a caller forgot to scope.
