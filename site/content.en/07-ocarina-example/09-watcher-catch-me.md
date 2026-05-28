---
title: "07.09 — catch_me_if_you_can"
description: "catch_me_if_you_can: the ocarina-example watcher that detects and logs stray elements popping up while a test runs."
weight: 9
date: 2026-05-20
series: ["ocarina-example"]
series_order: 9
tags: ["watcher"]
---

# 07.09&nbsp;—&nbsp;`catch_me_if_you_can`

> Detects parasite elements that pop on the page _while_ the test is running, and traces them.

## Callback

```python
# src/lib/ext/selenium/watchers/catch_me_if_you_can_watcher.py
def catch_me_if_you_can_cb(watcher: SeleniumWatcher) -> None:
    elements = watcher.driver.execute_script(
        "return Array.from(document.querySelectorAll('.catch-me-if-you-can'));"
    )

    if not elements:
        return

    raw = watcher.driver.execute_script(
        """
        return arguments[0].map(el => ({
            tag:       el.tagName.toLowerCase(),
            text:      el.innerText.trim(),
            id:        el.id,
            cls:       el.className,
            name:      el.getAttribute('name') || '',
            testid:    el.getAttribute('data-testid') || '',
        }));
        """,
        elements,
    )

    for attrs in raw:
        fingerprint = ":".join(
            filter(
                None,
                [
                    attrs["tag"],
                    attrs["text"],
                    attrs["id"],
                    attrs["cls"],
                    attrs["name"],
                    attrs["testid"],
                ],
            )
        )

        if fingerprint in watcher.cache:
            continue

        watcher.cache.add(fingerprint)
        watcher.report(
            f"catch-me-if-you-can element detected: <{attrs['tag']}> {attrs['text']!r}",
            label="CATCH_ME_IF_YOU_CAN",
        )
```

## Mechanics

### 1. Javascript to bypass implicit wait

```python
elements = watcher.driver.execute_script(
    "return Array.from(document.querySelectorAll('.catch-me-if-you-can'));"
)
```

Not `find_elements(By.CSS_SELECTOR, ...)`.

> Going straight through JavaScript bypasses all internal polling logic and keeps the watcher's execution as non-blocking as possible for the test running on the same driver.

(Holy Book, _handling-flakiness_.)

If the watcher used `find_elements(By.CSS_SELECTOR, ".catch-me-if-you-can")` with no matching element, Selenium would block for `--wait-timeout` seconds (typically 10s) before returning `[]`. At a poll rate of 0.8s, that breaks everything.

`querySelectorAll` in JavaScript is **synchronous and instant**&nbsp;—&nbsp;returns `[]` immediately if there's nothing.

### 2. Early return

```python
if not elements:
    return
```

Nothing found: return immediately. Next poll fires after `poll_interval`.

### 3. Attribute extraction in JS (single round-trip)

```python
raw = watcher.driver.execute_script(
    """
    return arguments[0].map(el => ({
        tag: el.tagName.toLowerCase(),
        text: el.innerText.trim(),
        ...
    }));
    """,
    elements,
)
```

Instead of 6 Selenium round-trips per element (`tag_name`, `text`, `get_attribute("id")`, ...), one JS call returns all attributes at once.

6 round-trips × 50ms = 300ms. One call = 50ms. That's a real difference at 800ms poll intervals.

### 4. Fingerprint

```python
fingerprint = ":".join(filter(None, [
    attrs["tag"], attrs["text"], attrs["id"], attrs["cls"], attrs["name"], attrs["testid"],
]))
```

For `<div class="catch-me-if-you-can" id="x" data-testid="y">Hello</div>`, fingerprint = `"div:Hello:x:catch-me-if-you-can:..."`.

`filter(None, ...)` removes empty strings&nbsp;—&nbsp;without it we'd get `"div:Hello:x::cls::y"` with double `::`.

### 5. Dedup

```python
if fingerprint in watcher.cache:
    continue

watcher.cache.add(fingerprint)
watcher.report(...)
```

Already reported this fingerprint → skip. `watcher.cache` is a `set[str]` that lives for the test's lifetime.

An element visible across 5 consecutive polls is reported **once**. No spam.

### 6. `watcher.report`

```python
watcher.report(
    f"catch-me-if-you-can element detected: <{attrs['tag']}> {attrs['text']!r}",
    label="CATCH_ME_IF_YOU_CAN",
)
```

`watcher.report`:

1. `logger.info(message)`: shows up in the watcher's logs.
2. `take_screenshot(driver, logger, label)`: takes a screenshot with label `CATCH_ME_IF_YOU_CAN`.

See [`../02-ocarina/07-watcher.md`](../02-ocarina/07-watcher.md) for the watcher mechanics.

## Taxonomy

```python
watcher_taxonomy = (*taxonomy[:-1], f"{test_name} - {watcher.name}")
scoped_logger = self._create_logger().set_domain_taxonomy(watcher_taxonomy)
watcher.start(driver, scoped_logger, self._take_screenshot)
```

With `FileLogger`, a distinct `.log` file is generated alongside the test's own log:

```
.ocarina_logs/
└── e2e/
    └── Randomness/
        └── Randomness/
            ├── Send the chaotic form.log                              # test log
            └── Send the chaotic form - catch-me-if-you-can.log        # watcher log
```

The DOCX test-proof plugin creates them side by side.

## On the scenario side

```python
test_send_chaotic_form = create_selenium_test(
    name="Send the chaotic form",
    test_scenario=lambda driver, logger: Scenario(
        test_chain=_send_chaotic_form(HumanizedDriver(driver, ...), logger),
        watchers=[
            create_selenium_watcher(
                callback=catch_me_if_you_can_cb,
                name="catch-me-if-you-can",
                poll_interval=0.8,
            ),
        ],
    ),
)
```

## "_Watchers only bring bad news_"

`CLAUDE.md`:

> **Watcher signals are negative-only.** A watcher that emits "_login succeeded_" breaks the contract.

Here a `.catch-me-if-you-can` element is friction we didn't want. A watcher must never say "all good"&nbsp;—&nbsp;**it either grumbles or stays silent** (Silence is Golden).

A positive signal ("the success toast appeared") belongs in `test_chain` via an `act`, not in a watcher.
