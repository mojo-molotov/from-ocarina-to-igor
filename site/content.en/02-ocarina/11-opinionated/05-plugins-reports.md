---
title: "02.11.05 — Report plugins"
description: "Ocarina's opt-in report plugins: pretty_print_results, results_to_json, generate_docx_proof and timing, runnable in sequence or in parallel."
weight: 5
date: 2026-05-20
series: ["opinionated"]
series_order: 5
tags: ["ocarina"]
---

# 02.11.05&nbsp;—&nbsp;Report plugins

> Source folder: [`src/ocarina/opinionated/plugins/reports/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/opinionated/plugins/reports)
>
> `pretty_print_results`, `results_to_json`, `generate_docx_proof`, `timing`. All opt-in. Run sequentially or in parallel via `run_plugins`.

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

| Aspect        | Detail                                                |
| ------------- | ----------------------------------------------------- |
| **Hierarchy** | 3 levels: campaign `•`, suite `>`, case `»`           |
| **Levels**    | `PASSED` (green), `FAILED` (red), `SKIPPED` (gray)    |
| **Error**     | Message + step number where it failed ("_At step 3_") |
| **Summary**   | Aggregated count at the bottom                        |

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

Filename is an 8-char hex UUID → 16⁸ ≈ 4 billion options. No collisions in practice. 500 safety retries.

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

1. **Creates a unique subdirectory** under `output_root` (4-char hex UUID).
2. **Walks the logs tree** (`logs_root/campaign/suite/test.log`).
3. **For each `.log`**: creates a `.docx`.
4. **Inside each `.docx`**:
   - Heading 1: campaign name.
   - Heading 2: suite name.
   - Heading 3: case name.
   - Body: log lines, with UTC dates converted to local time.
   - When a line contains `"Screenshot: <path>"`: inserts the image.

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

→ `[UTC_DATE::2026-05-18T09:42:31.123456+00:00]` becomes `[05/18/2026 | 11h42:31.123456]` (local time).

### Screenshot detection

```python
_DEFAULT_SCREENSHOT_NEEDLE = "Screenshot: "
```

Line containing this needle → extract the path, insert the image into the doc. Path cleanly truncated (UUID) when too long.

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

→ On exit from the `with`:

> Tests duration: 5 minutes and 23 seconds (323.45 seconds)

Notes:

- **`interrupted = True`** on `KeyboardInterrupt` or `WarmupTimeoutError`&nbsp;—&nbsp;we don't pollute the output with an interrupted run's timing.
- **`format_elapsed`**: human-readable format (`5 minutes and 23 seconds`).

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

Auto singular/plural. _Oxford-comma_-ish format ("_2 hours, 5 minutes and 3 seconds_").

## Parallel execution with `run_plugins`

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

- **1 plugin → sequential** (no point spawning a thread).
- **N plugins → ThreadPoolExecutor(max_workers=N)**: all in parallel.
- **No plugin can kill the others**: every plugin runs inside `_run_plugin`, which catches + logs via `exceptions_logger`.

`generate_docx_proof` can take 10s (log parsing, Word generation, image insertion); `generate_json_results` takes 0.1s. Together in parallel: ~10s, not 10.1s.

## Why `run_plugins` takes `results` _as an argument_

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

The user supplies a `run_plugins: Callable[[TestCycleResults], None]`:

```python
run_plugins=lambda results: run_plugins(
    lambda: generate_docx_proof(logs_root=..., output_root=..., logger=...),
    lambda: generate_json_results(results=results, output_dir=..., logger=...),
    exceptions_logger=...,
),
```

→ `run_plugins` (the _outer_ lambda) captures `results`. The _inner_ `run_plugins` (the framework function) runs the plugins.

Important case: `generate_docx_proof` _doesn't need_ `results` (it reads the logs tree from disk). `generate_json_results` _does_. The `(results) -> ...` lambda lets each plugin grab what it needs.
