---
title: "02.11.05 — Plugins de rapport"
description: "Les plugins de rapport opt-in d'Ocarina : pretty_print_results, results_to_json, generate_docx_proof et timing, exécutables en séquence ou en parallèle."
weight: 5
date: 2026-05-20
series: ["opinionated"]
series_order: 5
tags: ["ocarina"]
---

# 02.11.05&nbsp;—&nbsp;Plugins de rapport

> Dossier source&nbsp;: [`src/ocarina/opinionated/plugins/reports/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/opinionated/plugins/reports)
>
> `pretty_print_results`, `results_to_json`, `generate_docx_proof`, `timing`. Tous opt-in. Exécutables séquentiellement ou en parallèle via `run_plugins`.

## `pretty_print_results`

```python
# src/ocarina/opinionated/plugins/reports/pretty_print_results.py
def pretty_print_results(results: TestCycleResults, *, with_colors: bool = False) -> None:
    """Display the full test results."""
```

```
Campaign
• Suite
  > Test case 1
    » PASSED
  > Test case 2
    » FAILED
      → Error message
        ⫸ At step 3
  > Test case 3
    » SKIPPED

Test results:
1 FAILED | 1 PASSED | 1 SKIPPED
```

| Aspect         | Détail                                                         |
| -------------- | -------------------------------------------------------------- |
| **Hiérarchie** | 3 niveaux&nbsp;: campagne `•`, suite `>`, cas `»`              |
| **Niveaux**    | `PASSED` (vert), `FAILED` (rouge), `SKIPPED` (gris).           |
| **Erreur**     | Message + step number où ça a fail («&nbsp;_At step 3_&nbsp;») |
| **Summary**    | Comptage agrégé en bas                                         |

## `results_to_json`

```python
def generate_json_results(*, results: TestCycleResults, output_dir: Path, logger: ILogger) -> None:
    """Write test results to a JSON file in results_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    max_stem_length = 8
    max_attempts = 500
    for _ in range(max_attempts):
        filename = f"{uuid.uuid4().hex[:max_stem_length]}.json"
        file_path = output_dir / filename
        if not file_path.exists():
            break
    else:
        raise RuntimeError(f"Can't generate unique JSON filename in: {output_dir}.")
```

```json
{
  "Campaign": {
    "Suite": {
      "test_case": [
        {"status": "success" | "fail", "error": "..."},
        counter,
        metadata
      ]
    }
  }
}
```

```python
def _result_to_serializable(v: Any) -> dict[str, str]:
    if is_ok(v):
        return {"status": "success"}
    if is_fail(v):
        return {"status": "fail", "error": str(v.error)}
    raise TypeError(f"Expected Ok or Fail instances, but got: {type(v)}")
```

Le filename est un UUID hex de 8 chars&nbsp;→&nbsp;16⁸ ≈ 4 milliards d'options. Pas de collision dans la pratique. 500 retries de sécurité.

## `generate_docx_proof`

```python
def generate_docx_proof(
    *,
    logs_root: Path,
    output_root: Path,
    logger: ILogger,
) -> None:
    """Transform text log files from automated tests into formatted Word documents,
    including screenshots."""
```

1. **Crée un sous-répertoire unique** sous `output_root` (UUID hex 4 chars).
2. **Parcourt l'arbre de logs** (`logs_root/campaign/suite/test.log`).
3. **Pour chaque `.log`**&nbsp;: crée un `.docx`.
4. **Dans chaque `.docx`**&nbsp;:
   - Heading 1&nbsp;: nom de campagne.
   - Heading 2&nbsp;: nom de suite.
   - Heading 3&nbsp;: nom de cas.
   - Body&nbsp;: lignes des logs, avec dates UTC adaptées à l'heure locale.
   - Quand la ligne contient `"Screenshot: <path>"`&nbsp;: insère l'image.

```python
_DEFAULT_UTC_DATE_REGEX = re.compile(r"\[UTC_DATE::([^]]+)]")

def _replace_utc_date(line: str, *, utc_date_regex) -> str:
    def _repl(m: re.Match[str]) -> str:
        with suppress(Exception):
            return (
                datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
                .astimezone()
                .strftime("[%m/%d/%Y | %Hh%M:%S.%f]")
            )
        return m.group(0)
    return utc_date_regex.sub(_repl, line)
```

→ `[UTC_DATE::2026-05-18T09:42:31.123456+00:00]` devient `[05/18/2026 | 11h42:31.123456]` (heure locale).

### Détection des screenshots

```python
_DEFAULT_SCREENSHOT_NEEDLE = "Screenshot: "
```

Quand une ligne contient cette needle, on extrait le path, on insère l'image dans le doc. Le path est tronqué proprement (UUID) si trop long.

## `timing`

```python
from contextlib import contextmanager

@contextmanager
def timing(*, prefix: str = "Duration:", seconds_label: str = "seconds"):
    start = time.perf_counter()
    interrupted = False
    try:
        yield
    except (KeyboardInterrupt, WarmupTimeoutError):
        interrupted = True
        raise
    finally:
        if not interrupted:
            end = time.perf_counter()
            elapsed = end - start
            human_readable = format_elapsed(elapsed)
            p = f"{prefix} " if prefix else ""
            print(f"\n{p}{human_readable} ({elapsed:.2f} {seconds_label})")
```

```python
with timing(prefix="Tests duration:"):
    bootstrap(...)
```

→ À la sortie du `with`&nbsp;:

> Tests duration: 5 minutes and 23 seconds (323.45 seconds)

Notes&nbsp;:

- **`interrupted = True`** si `KeyboardInterrupt` ou `WarmupTimeoutError`&nbsp;: on ne pollue pas la sortie avec un temps de run interrompu.
- **`format_elapsed`**&nbsp;: format human-readable (`5 minutes and 23 seconds`).

## `format_elapsed`

```python
def format_elapsed(seconds: float) -> str:
    secs = int(seconds)
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    minutes, secs = divmod(secs, 60)

    parts = []
    if days: parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours: parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes: parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if secs or not parts:
        parts.append(f"{secs} second{'s' if secs > 1 else ''}")

    if len(parts) > 1:
        return ", ".join(parts[:-1]) + " and " + parts[-1]
    return parts[0]
```

Singulier/pluriel automatique. Format _Oxford comma_-ish («&nbsp;_2 hours, 5 minutes and 3 seconds_&nbsp;»).

## Exécution parallèle avec `run_plugins`

```python
def run_plugins(*plugins: Effect, exceptions_logger: ILogger) -> None:
    if not plugins:
        return

    def _run_plugin(plugin: Effect, exceptions_logger: ILogger) -> None:
        try:
            plugin()
        except Exception as exc:
            exceptions_logger.exception("The plugin failed.", exc=exc)

    if len(plugins) == 1:
        _run_plugin(plugins[0], exceptions_logger)
        return

    with ThreadPoolExecutor(max_workers=len(plugins)) as executor:
        futures = [executor.submit(_run_plugin, plugin, exceptions_logger) for plugin in plugins]
        for f in futures:
            f.result()
```

- **1 plugin&nbsp;→&nbsp;séquentiel** (pas la peine de spawn un thread).
- **N plugins&nbsp;→&nbsp;ThreadPoolExecutor(max_workers=N)**&nbsp;: tous en parallèle.
- **Aucun plugin ne tue les autres**&nbsp;: chaque plugin est wrappé dans `_run_plugin` qui catch + log via `exceptions_logger`.

`generate_docx_proof` peut prendre 10s (parse de logs, génération Word, insertion images), `generate_json_results` prend 0.1s. Les deux en parallèle prennent ~10s, pas 10.1s.

## Pourquoi `run_plugins` prend `results` _en argument_

```python
def bootstrap[T](
    *,
    test_cycle: TestCycle[T],
    run_plugins: Callable[[TestCycleResults], None],
    post_exec: Callable[[TestCycleResults], None] | None = None,
    saturate_workers: bool = True,
) -> None:
    results = test_cycle.run_all(saturate_workers=saturate_workers)
    run_plugins(results)
    if post_exec:
        post_exec(results)
```

L'utilisateur fournit un `run_plugins: Callable[[TestCycleResults], None]`&nbsp;:

```python
run_plugins=lambda results: run_plugins(
    lambda: generate_docx_proof(logs_root=..., output_root=..., logger=...),
    lambda: generate_json_results(results=results, output_dir=..., logger=...),
    exceptions_logger=...,
),
```

→ `run_plugins` (le _outer_, lambda) capture `results`. Le _inner_ `run_plugins` (la fonction du framework) exécute les plugins.

Cas important&nbsp;: `generate_docx_proof` _n'a pas besoin_ de `results` (il lit l'arbre de logs sur le disque). Mais `generate_json_results` _a besoin_ de `results`. La lambda `(results) -> ...` permet à chaque plugin de capturer ce dont il a besoin.
