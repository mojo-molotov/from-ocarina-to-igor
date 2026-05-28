---
title: "07.04 — Corsicamon scenarios"
description: "The Corsicamon scenarios of ocarina-example: API key entry, a one-in-five draw failure, transient_errors and POM-internal retries."
weight: 4
date: 2026-05-20
series: ["ocarina-example"]
series_order: 4
---

# 07.04&nbsp;—&nbsp;Corsicamon scenarios

> Igoristan's "_Corsican Pokédex (Corsicadex)_" page. API key input, random draw with 1/5 fail, `transient_errors` for `Error('lol')`, and POM-internal retries against "_Corsicamons loaded / network error_" states.

## Campaign

```python
# src/tests/campaigns/corsicamon.py
def create_igoristan_corsicamon_campaign(*, drivers_pool) -> TestCampaign:
    return TestCampaign(
        name="Corsicamon",
        suites=[
            create_corsicamon_happy_paths_test_suite(drivers_pool=drivers_pool),
            create_corsicamon_unhappy_paths_test_suite(drivers_pool=drivers_pool),
        ],
    )


def create_igoristan_corsicamon_smoke_campaign(*, drivers_pool) -> TestCampaign:
    return TestCampaign(
        name="Corsicamon - Smoke",
        suites=[create_corsicamon_smoke_tests_suite(drivers_pool=drivers_pool)],
    )
```

## Smoke test

```python
# tests/scenarios/corsicamon/enter_api_key.py
def scenario_enter_api_key_smoke(driver, logger):
    page = CorsicamonEnterApiKeyPage(driver=driver)
    ...
    return [
        drive_page(
            act(page, open_corsicamon_page)...,
            act(page, verify_enter_api_key_screen)...,
        ),
    ]


test_enter_api_key_smoke = create_selenium_test(
    name="Corsicamon - Smoke - enter API key screen visible",
    test_scenario=lambda driver, logger: Scenario(
        test_chain=scenario_enter_api_key_smoke(driver, logger)
    ),
)
```

Verifies the API key entry page appears. Fails → smoke fails → main campaigns skipped.

## Happy path: API key entry + draw + add

```python
# tests/scenarios/corsicamon/new_draw.py
def scenario_new_draw_happy_path(driver, logger):
    on_enter_key = CorsicamonEnterApiKeyPage(driver=driver)
    on_main = CorsicamonMainPage(driver=driver)
    env = create_env_getters()
    api_key = env.get_value("igor_api_key")

    return [
        drive_page(
            act(on_enter_key, open_corsicamon_page)...,
            act(on_enter_key, enter_api_key_with_retries(api_key, retries=10, logger=logger))...,
            act(on_enter_key, click_validate_api_key)...,
        ),
        drive_page(
            act(on_main, verify_main_page)...,
            act(on_main, wait_for_pokemons_or_error_with_retries(retries=10, logger=logger))...,
            act(on_main, verify_pokemons_displayed)...,
        ),
        drive_page(
            act(on_main, click_redraw_button)...,
            act(on_main, wait_for_pokemons_or_error_with_retries(...))...,
            act(on_main, verify_pokemons_displayed)...,
        ),
    ]
```

1. Open → enter API key → validate.
2. Wait for Corsicamons (with retries against the 1/5 fail).
3. Re-draw with retries.

## Handling the 1/5 fail

`corsicamon_main.py`:

```python
def wait_for_pokemons_or_error_with_retries(retries: int, logger: ILogger):
    def unwrapped(p: CorsicamonMainPage) -> CorsicamonMainPage:
        return p.wait_for_pokemons_or_error_with_retries(retries=retries, logger=logger)
    return unwrapped
```

`pages/corsicamon/main.py`:

```python
def wait_for_pokemons_or_error_with_retries(self, *, retries: int, logger: ILogger) -> CorsicamonMainPage:
    attempts = 1
    while attempts <= retries:
        try:
            WebDriverWait(self._driver, get_timeout()).until(
                lambda d: self._has_pokemons() or self._has_error()
            )
            break
        except TimeoutException:
            pass

        if self._has_error():
            logger.warning(f"Got error on attempt {attempts}/{retries}, retrying...")
            self._click_redraw_button()
            attempts += 1
            continue
        if self._has_pokemons():
            return self

    logger.info(f"Pokemons loaded after {attempts} attempts.")
    return self
```

Retry is internal to the POM. The outer scenario only sees success or failure.

The POM-internal retry pattern is documented in the AI project's `CLAUDE.md`:

> **`introduce-pom-retries`**&nbsp;—&nbsp;POM-internal retries, with split (first-try + with-retries).

## Unhappy paths

`tests/scenarios/corsicamon/…`

- Entering an invalid API key → verify the error message.
- ...

## Back to Igoristan

```python
# tests/scenarios/corsicamon/back_to_igoristan.py
def scenario_back_to_igoristan(driver, logger):
    page = CorsicamonEnterApiKeyPage(driver=driver)
    return [
        drive_page(
            act(page, open_corsicamon_page)...,
            act(page, click_back_to_igoristan)...,
        ),
    ]


test_back_to_igoristan = create_selenium_test(
    name="Corsicamon - Back to Igoristan",
    test_scenario=lambda driver, logger: Scenario(test_chain=scenario_back_to_igoristan(driver, logger)),
    post_test_scenarios_fragments=[verify_homepage],
)
```
