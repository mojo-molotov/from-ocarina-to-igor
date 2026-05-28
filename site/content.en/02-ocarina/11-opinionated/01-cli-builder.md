---
title: "02.11.01 — CliBuilder + CliArg + _SilentArgumentParser"
description: "CliBuilder, CliArg and the silent parser: Ocarina's declarative layer over argparse, with error aggregation and post-parse effects."
weight: 1
date: 2026-05-20
series: ["opinionated"]
series_order: 1
tags: ["ocarina"]
---

# 02.11.01&nbsp;—&nbsp;`CliBuilder` + `CliArg` + `_SilentArgumentParser`

> Source file: [`src/ocarina/opinionated/cli/builder.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/builder.py)
>
> Declarative overlay on top of `argparse`. _Aggregates_ validation errors, _rewrites_ the help output on error, and _registers_ post-parse effects.

## `_SilentArgumentParser`

```python
class _SilentArgumentParser(ArgumentParser):
    def error(self, message: str) -> Never:
        """Raise an error."""
        raise ValueError(message)
```

The standard `ArgumentParser` calls `sys.exit(2)` directly on error. With that turd of a default, you **can't** intercept and you **can't** aggregate multiple errors.

`_SilentArgumentParser` _reroutes_ errors as `ValueError`. So `CliBuilder.parse` can catch and aggregate them.

Note: `Never` (PEP 661) is more precise than `None` for a function that only ever `raise`s.

## `CliArg`

```python
class CliArg:
    def __init__(
        self,
        *flags: str,
        validate: ArgValidator | None = None,
        **argparse_kwargs: Any,
    ) -> None:
        self.flags = flags
        self.validate = validate
        self.argparse_kwargs = argparse_kwargs
```

| Field             | Role                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `flags`           | The names (`"--browser"`, `"--driver-path"`)                                               |
| `validate`        | Optional validator `(value) -> None` that raises if invalid                                |
| `argparse_kwargs` | Everything else: `type=`, `default=`, `choices=`, `help=`, `nargs=`, `action=`, `metavar=` |

## `CliBuilder.parse`

```python
def parse(self) -> Namespace:
    parser = _SilentArgumentParser(
        description=self._description,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    for arg in self._args:
        parser.add_argument(*arg.flags, **arg.argparse_kwargs)

    try:
        namespace = parser.parse_args()
    except ValueError as exc:
        print(_INVALID_CLI_ARGUMENTS, file=sys.stderr)
        print(f"🚫  {_ucfirst(str(exc))}", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(2)

    errors: list[str] = []

    for arg in self._args:
        if arg.validate is None:
            continue
        dest = arg.argparse_kwargs.get("dest") or arg.flags[-1].lstrip("-").replace("-", "_")
        value = getattr(namespace, dest)
        try:
            arg.validate(value)
        except Exception as exc:
            errors.append(str(exc))

    for effect in self._effects_factory(namespace):
        try:
            effect()
        except Exception as exc:
            errors.append(str(exc))
            if self._effects_fail_fast:
                break

    if errors:
        print(_INVALID_CLI_ARGUMENTS, file=sys.stderr)
        for err in errors:
            print(f"🚫  {_ucfirst(str(err))}", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(2)

    return namespace
```

### 1. Parsing

```python
try:
    namespace = parser.parse_args()
except ValueError as exc:
    print(_INVALID_CLI_ARGUMENTS, file=sys.stderr)
    print(f"🚫  {_ucfirst(str(exc))}", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    sys.exit(2)
```

argparse raises (you passed `--browser=banana` when `choices=["chrome", "firefox"]`) → we intercept, print a clear message ("🚫 _Argument --browser: invalid choice: 'banana'_"), print the help, and exit.

### 2. Validation

```python
for arg in self._args:
    if arg.validate is None:
        continue
    dest = arg.argparse_kwargs.get("dest") or arg.flags[-1].lstrip("-").replace("-", "_")
    value = getattr(namespace, dest)
    try:
        arg.validate(value)
    except Exception as exc:
        errors.append(str(exc))
```

### 3. Effects

```python
for effect in self._effects_factory(namespace):
    try:
        effect()
    except Exception as exc:
        errors.append(str(exc))
        if self._effects_fail_fast:
            break
```

- Store the parsed value in a `CliStore` (see [`02-cli-store-phantoms.md`](02-cli-store-phantoms.md)).
- Validate inter-arg consistency (mutex, dependencies).
- Register an `atexit` cleanup (`_create_dont_force_delete_tmp_dirs_effect`).

Note: `_effects_fail_fast=True` stops at the first failing effect.  
Default `False` → try everything, aggregate.

## Why this level of indirection rather than argparse directly

| Without `CliBuilder`                             | With `CliBuilder`                                 |
| ------------------------------------------------ | ------------------------------------------------- |
| argparse `sys.exit(2)` on the first invalid flag | Aggregation of all errors                         |
| Inline or nested validation                      | _Declarative_ validation (`CliArg(validate=...)`) |
| Post-parse effects written by hand               | `effects_factory(namespace) -> Effects`           |
| argparse interleaved with business logic         | Separation of concerns                            |

## Example (Selenium CLI)

```python
return CliBuilder(
    args=[
        CliArg("--driver-path", type=str, default="", help="Path to the Selenium driver"),
        CliArg("--profile-path", type=str, default=None, help="Path to the browser profile directory"),
        CliArg("--browser", type=str, default=None, choices=browser_choices, help="..."),
        CliArg("--not-headless", action="store_true", help="..."),
        CliArg("--workers", type=int, default=5, help="..."),
        CliArg("--logger", type=str, default="terminal+file", choices=LOGGERS_CHOICES, help="..."),
        CliArg("--wait-timeout", type=int, default=10, help="..."),
        CliArg("--dont-force-delete-tmp-dirs", action="store_true", help="..."),
        CliArg("--only", nargs="+", default=[], metavar="ID", help="..."),
        CliArg("--exclude", nargs="+", default=[], metavar="ID", help="..."),
    ],
    effects_factory=lambda ns: (
        lambda: store.set("driver_path", ns.driver_path),
        lambda: store.set("profile_path", ns.profile_path),
        # ... etc ...
        _create_validate_only_exclude_mutex_effect(ns),
        _create_validate_dependent_args_effect(ns),
        _create_validate_driver_path(ns),
        _create_dont_force_delete_tmp_dirs_effect(dont_force_delete_tmp_dirs=ns.dont_force_delete_tmp_dirs),
    ),
)
```

→ Important: the `lambda`s capture `ns` (the namespace) by _closure_. They're **deferred**&nbsp;—&nbsp;they only run when `parse()` iterates the effects. That's how `_create_validate_dependent_args_effect(ns)` can return an `Effect` that runs _after_ `ns` is fully initialized.
