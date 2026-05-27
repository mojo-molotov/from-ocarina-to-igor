---
title: "02.11.06 — bootstrap + run_plugins"
weight: 6
date: 2026-05-20
series: ["opinionated"]
series_order: 6
tags: ["ocarina"]
---

# 02.11.06&nbsp;—&nbsp;`bootstrap` + `run_plugins`

> Fichier source&nbsp;: [`src/ocarina/opinionated/launcher/bootstrap.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/launcher/bootstrap.py)
>
> Point d'entrée d'un projet Ocarina.  
> Trois étapes&nbsp;: `cycle.run_all → run_plugins → post_exec`.

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

## Ordre

```
1. cycle.run_all()  →  results
2. run_plugins(results)
3. post_exec(results) (optionnel)
```

| Étape | Effet                                     | Pourquoi cet ordre                                                               |
| ----- | ----------------------------------------- | -------------------------------------------------------------------------------- |
| 1     | Tous les tests s'exécutent                | On a besoin des `results` pour la suite                                          |
| 2     | Les plugins se lancent (DOCX, JSON, etc.) | Doit s'exécuter _avant_ `post_exec` car peut avoir besoin du temps de génération |
| 3     | Post-exec (pretty_print + sys.exit)       | _Dernière_ chose&nbsp;; après ça, le process est mort                            |

## Typage

```python
run_plugins: Callable[[TestCycleResults], None]
post_exec: Callable[[TestCycleResults], None] | None = None
```

- Les deux reçoivent les **`results`** en argument&nbsp;:

  ```python
  bootstrap(
      post_exec=_post_exec,                     # signature: (results) -> None
      test_cycle=create_e2e_test_cycle(drivers_pool),
      run_plugins=lambda results: run_plugins(  # signature: (results) -> None
          lambda: generate_docx_proof(...),                     # plugin (closure)
          lambda: generate_json_results(results=results, ...),  # plugin (closure capturant results)
          exceptions_logger=...,
      ),
  )
  ```

- **`post_exec` est optionnel**. S'il n'est pas fourni, on quitte juste après `run_plugins`.

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

| Propriété                           | Détail                                                              |
| ----------------------------------- | ------------------------------------------------------------------- |
| **Vide&nbsp;→&nbsp;no-op**          | `run_plugins()` ne fait rien.                                       |
| **1 plugin&nbsp;→&nbsp;séquentiel** | Pas de thread inutile.                                              |
| **N plugins&nbsp;→&nbsp;parallèle** | `ThreadPoolExecutor(max_workers=N)`.                                |
| **Pas de propagation d'exception**  | Chaque plugin est isolé&nbsp;; un fail log + les autres continuent. |

## `main.py`

`ocarina-example/src/main.py`&nbsp;:

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

1. Push le `CliStore` (parse + validation CLI).
2. Construit la `drivers_pool` à partir des valeurs CLI.
3. Crée un logger.
4. **Warm-up Redis** (`warmup_redis_client()`).
5. Définit `_post_exec` (pretty_print + `sys.exit(1)` si échec).
6. **`with timing(...)`**&nbsp;: mesure la durée totale.
7. **`bootstrap(...)`**&nbsp;: compose tout.
   - `test_cycle=create_e2e_test_cycle(drivers_pool)`&nbsp;: cycle e2e construit.
   - `run_plugins=lambda results: run_plugins(...)`&nbsp;: DOCX + JSON en parallèle, exceptions loguées.
   - `post_exec=_post_exec`&nbsp;: print + exit.

## `bootstrap` est typé generic `[T]`

```python
def bootstrap[T](
    *,
    test_cycle: TestCycle[T],
    ...
) -> None:
```

Le `[T]` est le type du driver. Permet à _mypy_ de vérifier que toutes les composantes ont le même type de driver. Mais&nbsp;: `bootstrap` lui-même ne fait rien avec `T`, il le _capture_ juste via `TestCycle[T]`.

## `try/except`&nbsp;: fuck you

| Si une exception remonte de… | Conséquence souhaitée                                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `test_cycle.run_all()`       | Crash du process (mauvaise config)                                                                              |
| `run_plugins(results)`       | Selon ce que fait l'utilisateur. Le `run_plugins` natif suppress les erreurs&nbsp;; un autre pourrait propager. |
| `post_exec(results)`         | Idem                                                                                                            |
