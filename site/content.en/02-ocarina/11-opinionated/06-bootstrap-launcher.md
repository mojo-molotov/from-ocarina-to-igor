---
title: "02.11.06 — bootstrap + run_plugins"
description: "bootstrap and run_plugins: the entry point of an Ocarina project, in three steps, cycle.run_all then run_plugins then post_exec."
weight: 6
date: 2026-05-20
series: ["opinionated"]
series_order: 6
tags: ["ocarina"]
---

# 02.11.06&nbsp;—&nbsp;`bootstrap` + `run_plugins`

> Source file: [`src/ocarina/opinionated/launcher/bootstrap.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/launcher/bootstrap.py)
>
> Entry point of an Ocarina project.  
> Three steps: `cycle.run_all → run_plugins → post_exec`.

## Code

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

## Order

```
1. cycle.run_all()  →  results
2. run_plugins(results)
3. post_exec(results) (optional)
```

| Step | Effect                              | Why this order                                                  |
| ---- | ----------------------------------- | --------------------------------------------------------------- |
| 1    | All tests run                       | We need `results` for the rest                                  |
| 2    | Plugins fire (DOCX, JSON, etc.)     | Must run _before_ `post_exec` since it can take generation time |
| 3    | Post-exec (pretty_print + sys.exit) | _Last_ thing&nbsp;—&nbsp;after this, the process is dead        |

## Typing

```python
run_plugins: Callable[[TestCycleResults], None]
post_exec: Callable[[TestCycleResults], None] | None = None
```

- Both receive the **`results`** as an argument:

  ```python
  bootstrap(
      post_exec=_post_exec,                     # signature: (results) -> None
      test_cycle=create_e2e_test_cycle(drivers_pool),
      run_plugins=lambda results: run_plugins(  # signature: (results) -> None
          lambda: generate_docx_proof(...),                     # plugin (closure)
          lambda: generate_json_results(results=results, ...),  # plugin (closure capturing results)
          exceptions_logger=...,
      ),
  )
  ```

- **`post_exec` is optional**. Absent → we exit right after `run_plugins`.

## `run_plugins`

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
        futures = [
            executor.submit(_run_plugin, plugin, exceptions_logger)
            for plugin in plugins
        ]
        for f in futures:
            f.result()
```

| Property                     | Detail                                                                        |
| ---------------------------- | ----------------------------------------------------------------------------- |
| **Empty → no-op**            | `run_plugins()` does nothing.                                                 |
| **1 plugin → sequential**    | No needless thread.                                                           |
| **N plugins → parallel**     | `ThreadPoolExecutor(max_workers=N)`.                                          |
| **No exception propagation** | Each plugin is isolated&nbsp;—&nbsp;a failure logs and the others keep going. |

## `main.py`

`ocarina-example/src/main.py`:

```python
if __name__ == "__main__":
    CliStoreSingleton().push(create_selenium_auto_cli_store())

    drivers_pool = create_selenium_drivers_pool(
        browser=get_browser(),
        driver_path=get_driver_path(),
        headless=get_headless(),
        wait_timeout=get_timeout(),
        max_size=get_max_workers(),
        profile_path=get_profile_path(),
    )

    logger = create_matching_logger(CliStoreSingleton().get("logger"))

    logger.info("Warming up the Redis client...")
    warmup_redis_client()
    logger.success("Redis client initialized!")

    def _post_exec(results: TestCycleResults) -> None:
        print()
        pretty_print_results(results, with_colors=True)
        if has_test_cycle_failed(results):
            sys.exit(1)

    with timing(prefix="Tests duration:"):
        bootstrap(
            post_exec=_post_exec,
            test_cycle=create_e2e_test_cycle(drivers_pool),
            run_plugins=lambda results: run_plugins(
                lambda: generate_docx_proof(
                    logs_root=get_default_log_dir() / E2E_CYCLE_NAME,
                    logger=create_matching_logger("terminal").set_domain_taxonomy(
                        ("Generate DOCX proofs plugin",)
                    ),
                    output_root=Path.cwd() / ".reports" / "tests_docx_output",
                ),
                lambda: generate_json_results(
                    results=results,
                    output_dir=Path.cwd() / ".reports" / "tests_json_output",
                    logger=create_matching_logger("terminal").set_domain_taxonomy(
                        ("Generate JSON report file plugin",)
                    ),
                ),
                exceptions_logger=PrintLogger()
                    .set_prefix(
                        lambda: concat_metadata(
                            format_utc_date_metadata_str,
                            format_current_thread_metadata_str,
                        )
                    )
                    .set_domain_taxonomy(("Post-execution plugins",)),
            ),
        )
```

1. Push the `CliStore` (CLI parse + validation).
2. Build the `drivers_pool` from the CLI values.
3. Create a logger.
4. **Warm-up Redis** (`warmup_redis_client()`).
5. Define `_post_exec` (pretty_print + `sys.exit(1)` if failed).
6. **`with timing(...)`**: measures total duration.
7. **`bootstrap(...)`**: composes everything.
   - `test_cycle=create_e2e_test_cycle(drivers_pool)`: e2e cycle built.
   - `run_plugins=lambda results: run_plugins(...)`: DOCX + JSON in parallel, exceptions logged.
   - `post_exec=_post_exec`: print + exit.

## `bootstrap` is generic-typed `[T]`

```python
def bootstrap[T](
    *,
    test_cycle: TestCycle[T],
    ...
) -> None:
```

`[T]` is the driver type. Lets _mypy_ check that all components share the same driver type. `bootstrap` itself does nothing with `T`&nbsp;—&nbsp;it just _captures_ it via `TestCycle[T]`.

## `try/except`: fuck you

| If an exception bubbles up from… | Desired consequence                                                                                 |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| `test_cycle.run_all()`           | Process crash (bad config)                                                                          |
| `run_plugins(results)`           | Depends on the user. The native `run_plugins` suppresses errors; another impl could propagate them. |
| `post_exec(results)`             | Same                                                                                                |
