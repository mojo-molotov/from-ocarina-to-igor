---
title: "07.05 — Randomness scenarios (4 levels)"
description: "The randomness scenarios of ocarina-example: four progressive levels of chaos that stress Ocarina further and further."
weight: 5
date: 2026-05-20
series: ["ocarina-example"]
series_order: 5
tags: ["watcher"]
---

# 07.05&nbsp;—&nbsp;Randomness scenarios (4 levels)

> Four progressive levels of chaos. We start simple, ramp up complexity, stress Ocarina more and more.

## Campaign

```python
# src/tests/campaigns/randomness.py
def create_igoristan_randomness_campaign(*, drivers_pool) -> TestCampaign:
    return TestCampaign(
        name="Randomness",
        suites=[create_randomness_test_suite(drivers_pool=drivers_pool)],
    )
```

## Suite

```python
# src/tests/suites/randomness.py
def create_randomness_test_suite(*, drivers_pool) -> TestSuite:
    return TestSuite(
        name="Randomness",
        tests=[
            test_random_error_page,                     # level 1
            test_random_loaders_page,                   # level 1
            test_dsed,                                  # level 2
            test_madness,                               # level 2
            test_chaotic_form,                          # level 3
            test_walkthrough,                           # level 4
        ],
        drivers_pool=drivers_pool,
    )
```

## Levels

| Level | Mechanic exercised             | Difficulty |
| ----- | ------------------------------ | ---------- |
| 1     | Base DSL (`drive_page`, `act`) | easy       |
| 2     | `match_page` / `when`          | medium     |
| 3     | `HumanizedDriver` + `Watcher`  | hard       |
| 4     | Multi-page chaotic walkthrough | hard       |

## Level 1&nbsp;—&nbsp;Random Error Page

```python
# tests/scenarios/randomness/level_1/random_error_page.py
def scenario_random_error_page(driver, logger):
    page = RandomErrorPage(driver=driver)
    return [
        drive_page(
            act(page, open_random_error_page)...,
            act(page, verify_random_error_page)...,
        ),
    ]


test_random_error_page = create_selenium_test(
    name="Random Error Page - smoke",
    test_scenario=lambda driver, logger: Scenario(test_chain=scenario_random_error_page(driver, logger)),
)
```

Deliberately flaky&nbsp;—&nbsp;exercises the `on_failure` hook.

## Level 1&nbsp;—&nbsp;Random Loaders

```python
def scenario_random_loaders_page(driver, logger):
    page = RandomLoadersPage(driver=driver)
    return [
        drive_page(
            act(page, open_random_loaders_page)...,
            act(page, verify_random_loaders_page)...,
        ),
    ]
```

Verifies the page shows up with the expected loaders. No specific loader asserted&nbsp;—&nbsp;just something.

## Level 2&nbsp;—&nbsp;DSED (Donkey Sausage Eater Detector)

```python
# tests/scenarios/randomness/level_2/dsed.py
def scenario_dsed(driver, logger):
    page_loading_or_result = DsedIdsBypassedPage(driver=driver)
    check_that_page = DsedMatchers(driver=driver)

    return [
        drive_page(act(page_loading_or_result, open_dsed_page)...),
        match_page(branches=[
            when(check_that_page.is_approved,
                 name="approved",
                 then=[drive_page(act(page_loading_or_result, verify_approved)...)]),
            when(check_that_page.is_disapproved,
                 name="disapproved",
                 then=[drive_page(act(page_loading_or_result, verify_disapproved)...)]),
        ]),
    ]
```

1. The page can render `Approved` (70%) or `Disapproved` (30%).
2. `match_page` branches by `is_approved` / `is_disapproved`.
3. Each branch verifies the corresponding render.

Notes:

- `is_approved` / `is_disapproved` are matcher methods on the `DsedMatchers` POM, distinct from the `verify` actions (Holy Book: matcher ≠ verify).
- `match_page` here is the project-adapted version (with `raised_exceptions=transient_errors`).

## Level 2&nbsp;—&nbsp;Madness

```python
# tests/scenarios/randomness/level_2/madness.py
def scenario_madness(driver, logger):
    on_madness = MadnessBasePage(driver=driver)
    check_that_page = MadnessMatchers(driver=driver)

    return [
        drive_page(act(on_madness, open_madness_page)...),
        match_page(branches=[
            when(check_that_page.has_cors,
                 name="cors",
                 then=[drive_page(act(MadnessCorsPage(driver=driver), verify_cors_story)...)]),
            when(check_that_page.has_this_is_bastia,
                 name="this_is_bastia",
                 then=[drive_page(act(MadnessThisIsBastiaPage(driver=driver), verify_this_is_bastia_story)...)]),
        ]),
    ]
```

Same pattern as DSED. Difference: each branch instantiates its own POM (`MadnessCorsPage`, `MadnessThisIsBastiaPage`) rather than sharing one.

## Level 3&nbsp;—&nbsp;Chaotic Form (with `HumanizedDriver` + `Watcher`)

```python
# tests/scenarios/randomness/level_3/chaotic_form.py
def _send_chaotic_form(driver, logger):
    on_chaotic_form = ChaoticFormPage(driver=driver)
    ...
    return [
        drive_page(
            act(on_chaotic_form, open_chaotic_form_page)...,
            act(on_chaotic_form, fill_form_with_humanized_typing)...,
            act(on_chaotic_form, submit_form)...,
            act(on_chaotic_form, verify_submission_success)...,
        ),
    ]


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

1. **`HumanizedDriver`** wraps the Selenium driver to simulate human typing (see [`07-humanized-driver.md`](07-humanized-driver.md)).
2. **`wpm=125`**, **`typo_rate=0.14`** (14% typos), etc.
3. **`watchers=[...]`**: runs a background daemon during the test.
4. **`catch_me_if_you_can_cb`**: catches parasite `.catch-me-if-you-can` elements (see [`09-watcher-catch-me.md`](09-watcher-catch-me.md)).
5. **`poll_interval=0.8`**: polls every 800 ms.
6. **`HumanizedDriver` passed in place of the driver**: all POM `find_element` calls go through it.

## Level 4&nbsp;—&nbsp;Walkthrough

```python
# tests/scenarios/randomness/level_4/walkthrough.py
def scenario_walkthrough(driver, logger):
    on_homepage = Homepage(driver=driver)
    return [
        drive_page(act(on_homepage, open_homepage)..., act(on_homepage, verify_homepage)...),
        # ... sequential opening of each Igoristan page ...
        # ... verification of their title ...
        # ... return to homepage ...
    ]
```

A full tour through every corner of Igoristan.

## `HumanizedDriver` instantiated from the outside

```python
test_scenario=lambda driver, logger: Scenario(
    test_chain=_send_chaotic_form(HumanizedDriver(driver, ...), logger),
    ...
)
```

- The real `driver` comes from the pool.
- Wrap it in `HumanizedDriver(driver, ...)`.
- Pass the wrapper to the scenario.
- All POMs receive the wrapper.

`pom._driver = humanized_driver`. When the POM calls `self._driver.find_element(...).send_keys(...)`, `humanized` intercepts and types slowly with typos.
