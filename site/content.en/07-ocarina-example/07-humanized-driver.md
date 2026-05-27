---
title: "07.07 — HumanizedDriver"
weight: 7
date: 2026-05-20
series: ["ocarina-example"]
series_order: 7
tags: ["selenium"]
---

# 07.07&nbsp;—&nbsp;`HumanizedDriver`

> Source file: [`src/lib/ext/selenium/humanize/proxy.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/selenium/humanize/proxy.py)
>
> Proxy pattern: wraps a Selenium `WebDriver` and intercepts only `find_element*` to return `WebElement`s whose `send_keys` are _humanized_ (slow typing with typos, hesitations, corrections).

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

### 1. Inherits from `WebDriver`

```python
class HumanizedDriver(WebDriver):
```

`HumanizedDriver` passes `isinstance(x, WebDriver)` checks.

### 2. `object.__init__(self)` instead of `super().__init__()`

```python
def __init__(self, driver: WebDriver, **keyboard_config) -> None:
    object.__init__(self)
    ...
```

It's a hack. `WebDriver.__init__` demands plenty of parameters (service, options, etc.). `object.__init__(self)` bypasses all that. The `isinstance` check still passes.

### 3. Only intercepts `find_element` and `find_elements`

Every other driver call goes through `__getattr__`. That's the only override:

```python
def find_element(self, ...) -> _HumanizedWebElement:
    element = self._driver.find_element(by, value)
    return _HumanizedWebElement(element, self._config)
```

Fetch the real element, wrap it in `_HumanizedWebElement`.

### 4. `__getattr__` for everything else

```python
def __getattr__(self, name: str):
    return getattr(self._driver, name)
```

If you call `humanized_driver.current_url`, `humanized_driver.title`, `humanized_driver.execute_script(...)`, etc., Python **automatically** delegates to the real `self._driver` via `__getattr__`.

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

`Unpack[KeyboardConfig]` (PEP 692) lets you **type** the `**kwargs` as a `TypedDict`. The checker verifies that `wpm=125, typo_rate=0.14, ...` are the right keys and right types.

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

Same pattern: intercepts `send_keys`, delegates the rest.

## `humanized_send_keys_with_config`

| Parameter                  | Effect                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------- |
| `wpm=125`                  | Delay between keystrokes ~ 480ms/word, so ~50ms/char                                |
| `typo_rate=0.14`           | 14% chance of hitting the wrong key                                                 |
| `hesitation_rate=0.02`     | 2% chance of a long pause between keystrokes                                        |
| `burst_rate=0.35`          | 35% chance of typing several letters in a fast burst                                |
| `late_correction_rate=0.6` | If a typo: 60% chance of noticing "_later_", erasing back to the typo, and resuming |

## Why humanize?

- **`ChaoticForm` throws random error toasts**: you need to take your time. `HumanizedDriver` catches more toast-related bugs than a pile of `sleep` calls. We invest extra test effort here because the behavior is hard to reproduce at machine speed.
- **Test like a human**: a form a human fills in isn't tested by a script typing at 10,000 wpm.
- **Surface timing bugs**: race conditions (validation triggered too early, etc.) show up under human-paced input, not instant key injection.

## Usage on the scenario side

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

`HumanizedDriver` goes into the scenario; the scenario passes it to POMs; POMs call `self._driver.find_element(...).send_keys(...)`; every `send_keys` is humanized.

## The (rejected) alternative: monkey-patch

Monkey-patching `WebElement.send_keys` globally would work too.

Rejected because:

- Global effect = unpredictable side effects across tests.
- Not typed.
- Can't be toggled per-test.

The proxy is **opt-in per scenario**&nbsp;—&nbsp;the right granularity. One of my mentors used to say: _"The right abstraction, at the right time."_
