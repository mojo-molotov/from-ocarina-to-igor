---
title: "02.04.02 — Catalogue des assertions builtin"
description: "Le catalogue des assertions builtin d'Ocarina : une vingtaine de prédicats directs, closures et HOF suivant un même contrat de validation."
weight: 2
date: 2026-05-20
series: ["invariants"]
series_order: 2
tags: ["ocarina"]
---

# 02.04.02&nbsp;—&nbsp;Catalogue des assertions builtin

> Fichier source&nbsp;: [`src/ocarina/dsl/invariants/assertions.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/assertions.py) ~25 prédicats.

Toutes les assertions suivent le **même contrat**&nbsp;:

- Soit un prédicat direct `(value: T) -> None` qui lève `InvariantViolationError` si le contrat n'est pas respecté.
- Soit une **closure** quand il faut passer un argument de configuration (`is_equal_to(cmp)`, etc.).
- Soit, exceptionnellement, une **higher-order function (HOF)** comme `each`, placée ici par pragmatisme (créer un fichier entier pour ce seul cas serait _overkill_).

## Tableau complet

| Assertion                          | Direct /&nbsp;closure /&nbsp;HOF | Domaine         | Description                                                                                                     |
| ---------------------------------- | -------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------- |
| `is_str(value)`                    | direct                           | `Any`           | Lève si `value` n'est pas une `str`                                                                             |
| `is_none(value)`                   | direct                           | `Any`           | Lève si `value is not None`                                                                                     |
| `is_not_none(value)`               | direct                           | `Any`           | Lève si `value is None`                                                                                         |
| `is_equal_to(cmp)`                 | closure                          | `Any`           | Retourne `(value) -> None` qui lève si `value != cmp`                                                           |
| `is_not_equal_to(cmp)`             | closure                          | `Any`           | Retourne `(value) -> None` qui lève si `value == cmp`                                                           |
| `is_less_than(cmp)`                | closure                          | `float`         | `value < cmp`                                                                                                   |
| `is_less_than_or_equal_to(cmp)`    | closure                          | `float`         | `value <= cmp`                                                                                                  |
| `is_greater_than(cmp)`             | closure                          | `float`         | `value > cmp`                                                                                                   |
| `is_greater_than_or_equal_to(cmp)` | closure                          | `float`         | `value >= cmp`                                                                                                  |
| `is_positive(value)`               | direct                           | `float`         | `value >= 0`                                                                                                    |
| `is_not_zero(value)`               | direct                           | `float`         | `value != 0`                                                                                                    |
| `is_in(elements)`                  | closure                          | `Any`           | `value in tuple(elements)`                                                                                      |
| `is_file(value)`                   | direct                           | `str \| Path`   | `Path(value).is_file()`                                                                                         |
| `is_dir(value)`                    | direct                           | `str \| Path`   | `Path(value).is_dir()`                                                                                          |
| `is_iso_date_string(value)`        | direct                           | `str`           | `datetime.fromisoformat(value)`                                                                                 |
| `is_iso_utc_date_string(value)`    | direct                           | `str`           | Vérifie ISO + `tzinfo == UTC`                                                                                   |
| `is_email(value)`                  | direct                           | `str`           | Pas d'espace, exactement 1 `@`, parts non vides, domaine contient `.`                                           |
| `has_unique_elements(*, key=None)` | closure                          | `Iterable[Any]` | Détecte les doublons (lève `DuplicatesError`). Type-strict (`1 ≠ True`), supporte les unhashables.              |
| `is_empty(value)`                  | direct                           | `Sized`         | `len(value) == 0`                                                                                               |
| `is_truthy(value)`                 | direct                           | `Any`           | `bool(value) is True`                                                                                           |
| `is_valid_filename(value)`         | direct                           | `str`           | Cross-platform&nbsp;: chars interdits, mots réservés Windows, pas leading/trailing space ni dot, longueur ≤ 255 |
| `each(predicate)`                  | **HOF**                          | `Iterable[Any]` | Applique `predicate` à chaque élément                                                                           |

## Quelques implémentations en détail

### `is_email`

```python
def is_email(value: str) -> None:
    """Assert that the string is a valid email address (fast check)."""
    if " " in value:
        raise InvariantViolationError(f"'{value}' must not contain whitespace.")
    if value.count("@") != 1:
        raise InvariantViolationError(f"'{value}' must contain exactly one '@' character.")
    local_part, domain_part = value.split("@")
    if not local_part or not domain_part:
        raise InvariantViolationError(f"'{value}' must have non-empty local and domain parts.")
    if "." not in domain_part:
        raise InvariantViolationError(f"Domain part of '{value}' must contain at least one '.'.")
```

Quatre vérifications minimales. Pas de regex RFC5322. C'est volontaire&nbsp;: l'auteur fait le pari que la validation _exhaustive_ d'un email se fait en envoyant un email, pas en regex.

### `has_unique_elements`

```python
def has_unique_elements(*, key: Callable[[Any], Any] | None = None):
    def unwrapped(value: Iterable[Any]) -> None:
        items = list(value)
        key_fn = key or (lambda x: x)

        seen: list[tuple[type, Any]] = []
        duplicates = []

        for item in items:
            keyed = key_fn(item)
            typed_key = (type(keyed), keyed)

            found = False
            for seen_key in seen:
                if typed_key[0] == seen_key[0] and typed_key[1] == seen_key[1]:
                    found = True
                    if keyed not in duplicates:
                        duplicates.append(keyed)
                    break

            if not found:
                seen.append(typed_key)

        if duplicates:
            raise DuplicatesError(duplicates)
    return unwrapped
```

1. **Type-strict**&nbsp;: `(type(keyed), keyed)` est la clé de comparaison. Conséquence&nbsp;: `1`, `1.0`, et `True` sont _différents_ (ils ont des types différents). En Python idiomatique, `1 == True` est vrai, mais ici on s'en moque&nbsp;: on veut différencier.
2. **Supporte les unhashables**&nbsp;: on compare en O(n²) avec une liste plutôt qu'un set. Mais on peut hasher (`list`, `dict`, `set` comme valeurs sont OK).
3. **Lève un `DuplicatesError`**&nbsp;: sous-classe de `InvariantViolationError`, qui formate joliment la liste des doublons.

Utilisé pour valider l'unicité des noms de tests /&nbsp;IDs. Depuis `1.1.10`, les validateurs de noms (campagnes, suites, cas) fournissent une `key` qui normalise le nom en NFC puis lui applique `casefold`&nbsp;: l'unicité des **noms** devient insensible à la casse (`Login` et `login` forment un doublon), tandis que l'unicité des **IDs** reste exacte.

### `is_valid_filename`

```python
def is_valid_filename(value: str) -> None:
    _forbidden_chars = re.compile(r'[\x00-\x1f\\/:*?"<>|]')
    _windows_reserved = re.compile(
        r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", re.IGNORECASE
    )

    if not value:
        raise InvariantViolationError("Filename must not be empty.")
    if len(value) > 255:
        raise InvariantViolationError(f"Filename '{value}' exceeds 255 characters.")
    if _forbidden_chars.search(value):
        raise InvariantViolationError(
            f"Filename '{value}' contains forbidden characters "
            '(control chars or one of: \\ / : * ? " < > |).'
        )
    if value[0] in (".", " ") or value[-1] in (".", " "):
        raise InvariantViolationError(f"Filename '{value}' must not start or end with a dot or a space.")

    stem = value.split(".", 1)[0]
    if _windows_reserved.match(stem):
        raise InvariantViolationError(f"Filename '{value}' uses a reserved Windows device name.")
```

1. Chars interdits (contrôle + `\ / : * ? " < > |`)
2. Pas de leading/trailing `.` ou ` `
3. Pas de mot réservé par Windows (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`)
4. Longueur comprise entre 1 et 255

Utilisé pour valider les noms de tests, parce que **chaque test produit un fichier .log** dont le nom dérive du nom du test. Voir [`validate_test_runners_names`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_runners_names.py)

### `is_iso_utc_date_string`

```python
def is_iso_utc_date_string(value: str) -> None:
    try:
        dt = datetime.fromisoformat(value)
    except Exception as exc:
        raise InvariantViolationError(f"'{value}' is not a valid ISO date string.") from exc
    if dt.tzinfo != UTC:
        raise InvariantViolationError(f"'{value}' is not in UTC (tz={dt.tzinfo}).")
```

Accepte `"2025-12-18T10:30:00+00:00"`, `"2025-12-18T10:30:00Z"`. Refuse `"2025-12-18"` (pas de timezone) et `"2025-12-18T10:30:00+02:00"` (pas UTC).

Utilisé côté `ocarina-example` pour valider l'`OTP_CACHE_DATE` lu depuis le cache L1.

### `each`

```python
def each(predicate: Predicate[Any]) -> Predicate[Iterable[Any]]:
    def unwrapped(value: Iterable[Any]) -> None:
        for item in value:
            predicate(item)
    return unwrapped
```

```python
validate(filenames).assert_that(each(is_valid_filename)).execute().raise_if_invalid()
```

## Comment écrire son propre prédicat

Cas direct&nbsp;:

```python
def is_str(value: Any) -> None:
    if not isinstance(value, str):
        raise InvariantViolationError("Expected value to be string.")
```

Cas paramétré&nbsp;:

```python
def is_equal_to(cmp: Any) -> Predicate[Any]:
    def unwrapped(value: Any) -> None:
        if value != cmp:
            raise InvariantViolationError(f"{value} is not equal to {cmp}.")
    return unwrapped
```

1. Lever **`InvariantViolationError`** (jamais une autre exception).
2. Le message doit être **diagnostiquable**&nbsp;: inclure `value`, `cmp`, contexte utile.
3. Le prédicat est une `Callable[[T], None]`.
