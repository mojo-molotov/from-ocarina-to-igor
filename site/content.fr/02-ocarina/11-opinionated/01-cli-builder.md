---
title: "02.11.01 — CliBuilder + CliArg + _SilentArgumentParser"
weight: 1
date: 2026-05-20
series: ["opinionated"]
series_order: 1
tags: ["ocarina"]
---

# 02.11.01&nbsp;—&nbsp;`CliBuilder` + `CliArg` + `_SilentArgumentParser`

> Fichier source&nbsp;: [`src/ocarina/opinionated/cli/builder.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/builder.py)
>
> Surcouche déclarative au-dessus d'`argparse`. Permet d'_agréger_ les erreurs de validation, _ré-écrire_ la sortie d'aide en cas d'erreur, et _enregistrer_ des effets post-parse.

## `_SilentArgumentParser`

```python
class _SilentArgumentParser(ArgumentParser):
    def error(self, message: str) -> Never:
        """Raise an error."""
        raise ValueError(message)
```

L'`ArgumentParser` standard appelle `sys.exit(2)` directement en cas d'erreur. Avec cette merde, on **ne peut pas** intercepter, on **ne peut pas** agréger plusieurs erreurs.

`_SilentArgumentParser` _re-route_ les erreurs en `ValueError`. Donc `CliBuilder.parse` peut les attraper et les agréger.

Note&nbsp;: le type de retour `Never` (PEP 661) est plus précis que `None` dans le cas d'une fonction qui ne fait que `raise` systématiquement.

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

| Champ             | Rôle                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| `flags`           | Les noms (`"--browser"`, `"--driver-path"`)                                                          |
| `validate`        | Validator optionnel `(value) -> None` qui lève si invalide                                           |
| `argparse_kwargs` | Tout le reste&nbsp;: `type=`, `default=`, `choices=`, `help=`, `nargs=`, `action=`, `metavar=`, etc. |

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

Si argparse lève (parce qu'on lui a passé `--browser=banana` alors que `choices=["chrome", "firefox"]`), on intercepte, on affiche un message clair («&nbsp;🚫 _Argument --browser: invalid choice: 'banana'_&nbsp;»), on imprime l'help, on quitte.

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

### 3. Effets

```python
for effect in self._effects_factory(namespace):
    try:
        effect()
    except Exception as exc:
        errors.append(str(exc))
        if self._effects_fail_fast:
            break
```

- Stocker la valeur parsée dans un `CliStore` (cf. [`02-cli-store-phantoms.md`](02-cli-store-phantoms.md)).
- Valider la cohérence inter-args (mutex, dépendances).
- Enregistrer un `atexit` cleanup (`_create_dont_force_delete_tmp_dirs_effect`).

Note&nbsp;: si `_effects_fail_fast` vaut `True`, on s'arrête au premier effet en erreur.  
Par défaut, `False`&nbsp;→&nbsp;on tente tout et on agrège.

## Pourquoi ce niveau d'indirection plutôt qu'argparse direct

| Sans `CliBuilder`                               | Avec `CliBuilder`                                 |
| ----------------------------------------------- | ------------------------------------------------- |
| argparse `sys.exit(2)` au premier flag invalide | Aggrégation de toutes les erreurs                 |
| Validation inline ou imbriquée                  | Validation _déclarative_ (`CliArg(validate=...)`) |
| Effets post-parse écrits à la main              | `effects_factory(namespace) -> Effects`           |
| Imbrication argparse + logique métier           | Séparation des concerns                           |

## Exemple (Selenium CLI)

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

→ Note importante&nbsp;: les `lambda` capturent `ns` (le namespace) en _closure_. Elles sont **différées**&nbsp;; elles ne s'exécutent que quand `parse()` itère sur les effets. C'est ce qui permet à `_create_validate_dependent_args_effect(ns)` de retourner un `Effect` qui sera appelé _après_ que `ns` est complètement initialisé.
