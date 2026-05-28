---
title: "07.07 — HumanizedDriver"
description: "HumanizedDriver : un proxy de WebDriver qui humanise la frappe, lenteur, typos et corrections, en interceptant les find_element."
weight: 7
date: 2026-05-20
series: ["ocarina-example"]
series_order: 7
tags: ["selenium"]
---

# 07.07&nbsp;—&nbsp;`HumanizedDriver`

> Fichier source&nbsp;: [`src/lib/ext/selenium/humanize/proxy.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/selenium/humanize/proxy.py)
>
> Proxy pattern&nbsp;: wrappe un `WebDriver` Selenium et intercepte uniquement `find_element*` pour retourner des `WebElement` qui font des `send_keys` _humanisés_ (frappe lente avec typos, hésitations, corrections).

## Code

```python
class HumanizedDriver(WebDriver):
    def __init__(self, driver: WebDriver, **keyboard_config: Unpack[KeyboardConfig]) -> None:
        object.__init__(self)
        self._driver = driver
        self._config = keyboard_config

    def find_element(self, by: str | RelativeBy = "id", value: str | None = None) -> _HumanizedWebElement:
        element = self._driver.find_element(by, value)
        return _HumanizedWebElement(element, self._config)

    def find_elements(self, by: str | RelativeBy = "id", value: str | None = None) -> list[WebElement]:
        elements = self._driver.find_elements(by, value)
        return [_HumanizedWebElement(el, self._config) for el in elements]

    def __getattr__(self, name: str):
        return getattr(self._driver, name)
```

### 1. Hérite de `WebDriver`

```python
class HumanizedDriver(WebDriver):
```

`HumanizedDriver` _passe_ le _type check_ `isinstance(x, WebDriver)`.

### 2. `object.__init__(self)` au lieu de `super().__init__()`

```python
def __init__(self, driver: WebDriver, **keyboard_config) -> None:
    object.__init__(self)
    ...
```

C'est un hack. `WebDriver.__init__` exige plein de paramètres (service, options, etc.). On _bypass_ via `object.__init__(self)` pour éviter de devoir passer ces paramètres. L'_isinstance check_ passe quand même.

### 3. Intercepte _uniquement_ `find_element` et `find_elements`

Tous les autres appels au driver passent par `__getattr__`. C'est l'unique surcharge&nbsp;:

```python
def find_element(self, ...) -> _HumanizedWebElement:
    element = self._driver.find_element(by, value)
    return _HumanizedWebElement(element, self._config)
```

→ On récupère l'élément réel, on l'enrobe dans `_HumanizedWebElement`.

### 4. `__getattr__` pour tout le reste

```python
def __getattr__(self, name: str):
    return getattr(self._driver, name)
```

Si on appelle `humanized_driver.current_url`, `humanized_driver.title`, `humanized_driver.execute_script(...)`, etc., Python délègue **automatiquement** au `self._driver` réel via `__getattr__`.

### 5. `**keyboard_config: Unpack[KeyboardConfig]`

```python
class KeyboardConfig(TypedDict):
    wpm: float
    typo_rate: float
    hesitation_rate: float
    burst_rate: float
    late_correction_rate: float


def __init__(self, driver: WebDriver, **keyboard_config: Unpack[KeyboardConfig]) -> None:
    ...
```

`Unpack[KeyboardConfig]` (PEP 692) permet de **typer** les `**kwargs` comme un `TypedDict`. Le checker vérifie que `wpm=125, typo_rate=0.14, ...` sont les bonnes clés et bons types.

## `_HumanizedWebElement`

```python
class _HumanizedWebElement(WebElement):
    def __init__(self, element: WebElement, keyboard_config: KeyboardConfig) -> None:
        self._element = element
        self._config = keyboard_config

    def send_keys(self, *value: str | int | None) -> None:
        humanized_send_keys_with_config(self._element, *value, **self._config)

    def __getattr__(self, name: str):
        return getattr(self._element, name)
```

Même pattern&nbsp;: intercepte `send_keys`, délègue le reste.

## `humanized_send_keys_with_config`

| Paramètre                  | Effet                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `wpm=125`                  | Délai entre frappes ~ 480ms /&nbsp;mot, donc ~50ms/char                                                                              |
| `typo_rate=0.14`           | 14% de chance de taper la mauvaise touche                                                                                            |
| `hesitation_rate=0.02`     | 2% de chance d'une pause longue entre frappes                                                                                        |
| `burst_rate=0.35`          | 35% de chance de taper plusieurs lettres en burst rapide                                                                             |
| `late_correction_rate=0.6` | Si typo&nbsp;: 60% de chance de s'en rendre compte «&nbsp;_plus tard_&nbsp;», de tout effacer jusqu'à la typo et reprendre la saisie |

## Pourquoi humaniser&nbsp;?

- **Le `ChaoticForm` de l'Igoristan affiche des toasts d'erreurs aléatoires**&nbsp;: il faut prendre son temps dessus. Si de nouveaux bugs du même genre apparaissent, un `HumanizedDriver` les détecte mieux que de gros `sleep` posés «&nbsp;_le temps d'attendre un toast_&nbsp;». On est vigilant sur ce formulaire et on y consacre davantage d'effort de test parce qu'on sait qu'il a des comportements indésirables, difficiles à reproduire en testant «&nbsp;_juste_&nbsp;» le parcours rapidement.
- **Tester comme un humain réel**&nbsp;: un formulaire qu'un humain remplit n'est pas testé avec un humain qui tape 10&nbsp;000 mots/minute.
- **Faire émerger les bugs de timing**&nbsp;: si l'UI a une race condition (validation déclenchée trop tôt, etc.), elle apparaît avec une saisie humaine, pas avec une saisie ultra-rapide.

## Usage côté scénario

```python
test_send_chaotic_form = create_selenium_test(
    name="Send the chaotic form",
    test_scenario=lambda driver, logger: Scenario(
        test_chain=_send_chaotic_form(
            HumanizedDriver(
                driver,
                wpm=125,
                typo_rate=0.14,
                hesitation_rate=0.02,
                burst_rate=0.35,
                late_correction_rate=0.6,
            ),
            logger,
        ),
        watchers=[create_selenium_watcher(callback=catch_me_if_you_can_cb, name="catch-me-if-you-can", poll_interval=0.8)],
    ),
)
```

`HumanizedDriver` est **passé au scénario**&nbsp;; le scénario le passe aux POMs&nbsp;; les POMs font `self._driver.find_element(...).send_keys(...)`&nbsp;; chaque `send_keys` est humanisé.

## L'alternative (rejetée)&nbsp;: monkey-patch

On aurait pu monkey-patcher `WebElement.send_keys` au niveau global.

Refusé, parce que&nbsp;:

- Effet global = effets de bord imprévisibles dans d'autres tests.
- Pas typé.
- Pas activable/désactivable par test.

Le proxy est **opt-in par scénario**, _c'est la bonne granularité._  
L'un de mes mentors disait&nbsp;: _"La bonne abstraction, au bon moment."_
