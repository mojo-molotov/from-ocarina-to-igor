---
title: "07.03 — Scénarios Dashboard login"
description: "Trois familles : happy paths, unhappy paths, data-driven multi-login. Tous exercent le useAuth à 10% de raté et la coordination OTP."
weight: 3
date: 2026-05-20
series: ["ocarina-example"]
series_order: 3
tags: ["scenarios", "otp"]
---

# 07.03&nbsp;—&nbsp;Scénarios Dashboard login

> Trois familles&nbsp;: happy paths, unhappy paths, data-driven multi-login. Tous exercent le `useAuth` à 10% de raté et la coordination OTP.

## `dashboard_login`

```python
# src/tests/campaigns/dashboard_login.py
def create_igoristan_login_campaign(*, drivers_pool: SeleniumWebDriversPool) -> TestCampaign:
    return TestCampaign(
        name="Dashboard login",
        suites=[
            create_igoristan_login_happy_paths_test_suite(drivers_pool=drivers_pool),
            create_igoristan_login_unhappy_paths_test_suite(drivers_pool=drivers_pool),
            create_igoristan_login_data_driven_test_suite(drivers_pool=drivers_pool),
        ],
    )
```

## Happy paths

```python
# src/tests/suites/dashboard/access/happy_paths.py
def create_igoristan_login_happy_paths_test_suite(*, drivers_pool) -> TestSuite:
    return TestSuite(
        name="Login happy paths",
        tests=[
            test_dashboard_login_without_otp_happy_path,
            test_dashboard_login_with_otp_happy_path,
            test_dashboard_login_page_back_to_igoristan_button,
        ],
        drivers_pool=drivers_pool,
    )
```

### Test 1&nbsp;: login sans OTP

```python
def dashboard_login_without_otp_happy_path(driver, logger):
    dashboard_creds = create_env_getters().get_credentials("dashboard")
    on_dashboard_login_page = DashboardLoginPage(driver=driver)
    on_dashboard_welcome_page = DashboardWelcomePage(driver=driver)

    just_log_error = create_just_log_error(logger=logger)
    log_error_with_current_url = create_log_error_with_current_url(logger=logger, driver=driver)
    just_log_success = create_just_log_success(logger=logger)
    log_success_with_current_url_and_take_screenshot = create_log_success_with_current_url_and_take_screenshot(...)

    retries_amount = max(get_max_workers(), 10)

    return [
        drive_page(
            act(on_dashboard_login_page, open_dashboard_login_page)
                .failure(just_log_error("Failed to open the dashboard login page..."))
                .success(just_log_success("Opened the dashboard login page!")),
            act(on_dashboard_login_page, verify_dashboard_login_page)
                .failure(log_error_with_current_url("Failed to verify..."))
                .success(log_success_with_current_url_and_take_screenshot("Verified!")),
            act(on_dashboard_login_page,
                login_without_otp_and_with_retries(dashboard_creds, retries_amount, logger=logger))
                .failure(just_log_error("Failed to connect to the dashboard without OTP..."))
                .success(just_log_success("Connected to the dashboard!")),
        ),
        drive_page(
            act(on_dashboard_welcome_page, verify_dashboard_welcome_page)
                .failure(log_error_with_current_url("Failed to verify..."))
                .success(log_success_with_current_url_and_take_screenshot("Verified!")),
        ),
    ]
```

1. **`retries_amount = max(get_max_workers(), 10)`**&nbsp;: on rejoue le login interne (au POM) au moins 10 fois, à cause des 10% d'échec aléatoire.
2. **`login_without_otp_and_with_retries(creds, retries_amount, logger=logger)`**&nbsp;: closure qui capture creds + nb retries + logger. Le connector retourne `Callable[[DashboardLoginPage], DashboardLoginPage]`.
3. **2 `drive_page`**&nbsp;: login + welcome page. Chacun ouvre, vérifie, screenshot.
4. **Log factories partout**&nbsp;: aucune lambda inline.
5. **`SeleniumTitleMixin` côté POM**&nbsp;: `get_current_title()` est utilisé par le hook `on_failure` de `act`.

### Test 2&nbsp;: login avec OTP

```python
def dashboard_login_with_otp_happy_path(driver, logger):
    # ... setup pareil ...

    cache = in_memory_cache_with_30m_ttl
    fresh_cache_key_for_username = reserve_free_cache_key(cache)
    fresh_cache_key_for_otp_send_button_click_date = reserve_free_cache_key(cache)

    return [
        drive_page(
            act(on_dashboard_login_page, open_dashboard_login_page)...,
            act(on_dashboard_login_page, verify_dashboard_login_page)...,
            act(on_dashboard_login_page,
                start_to_login_with_otp_and_with_retries(
                    dashboard_creds, retries_amount,
                    cache=cache, logger=logger,
                    username_cache_key=fresh_cache_key_for_username,
                    otp_send_button_click_date_cache_key=fresh_cache_key_for_otp_send_button_click_date,
                ))...,
            act(on_dashboard_login_page, verify_otp_screen)...,
            act(on_dashboard_login_page,
                type_otp_with_retries(
                    retries_amount,
                    cache=cache, logger=logger,
                    username_cache_key=fresh_cache_key_for_username,
                    otp_send_button_click_date_cache_key=fresh_cache_key_for_otp_send_button_click_date,
                ))...,
        ),
        drive_page(
            act(on_dashboard_welcome_page, verify_dashboard_welcome_page)...,
            act(on_dashboard_welcome_page, click_on_go_to_nested_page_btn)...,
        ),
        drive_page(
            act(on_dashboard_protected_page, verify_dashboard_protected_page)...,
        ),
    ]
```

Trois `drive_page`. Cinq `act` dans le premier. Cache L1 + clés réservées pour partager des valeurs entre acts (cf. [`08-caches-locks.md`](08-caches-locks.md)).

### Test 3&nbsp;: back to Igoristan button

Test simple&nbsp;: sur la dashboard login page, cliquer sur «&nbsp;_Back to Igoristan_&nbsp;» et vérifier qu'on est revenu à la homepage. Utilise `post_test_scenarios_fragments=[verify_homepage]`.

## Unhappy paths

`tests/scenarios/dashboard/access/unhappy_paths.py`

- Login avec mauvais mot de passe&nbsp;→&nbsp;erreur affichée.
- Accès à `/dashboard/nested` _sans_ login&nbsp;→&nbsp;redirection.
- Accès à `/dashboard/nested` _avec_ login _sans_ OTP&nbsp;→&nbsp;message «&nbsp;_Access requires OTP_&nbsp;».

Le 3e cas utilise `pre_test_scenarios_fragments=[login_without_otp_happy_path]`&nbsp;:

```python
test_cant_access_the_protected_page_without_otp_using_the_ui = create_selenium_test(
    name="Can't access the protected page without OTP (using the UI)",
    test_scenario=lambda driver, logger: Scenario(
        test_chain=dashboard_access_to_protected_page_without_otp_using_the_ui(driver, logger)
    ),
    pre_test_scenarios_fragments=[login_without_otp_happy_path],
)
```

→ Le **fragment** `login_without_otp_happy_path` est exécuté avant le test. Le test commence donc en étant déjà loggé sans OTP.

## Data-driven multi-login

```python
# tests/scenarios/dashboard/data_driven/datasets/multi_login.py
multi_login_dataset: Sequence[MappingProxyType[ImmutableCredentialsKeys, str]] = [
    MappingProxyType({"login": "any", "password": "figatellu"}),
    MappingProxyType({"login": "Napoleon", "password": "figatellu"}),
    MappingProxyType({"login": "NoSicilianAllowed", "password": "figatellu"}),
    MappingProxyType({"login": "anonymous", "password": "figatellu"}),
    MappingProxyType({"login": "TheEmpire", "password": "figatellu"}),
]
```

Cinq logins différents (tous valides&nbsp;: `figatellu` est un passe-partout).  
Chaque combinaison génère un test&nbsp;:

```python
# tests/scenarios/dashboard/data_driven/multi_login.py
def _create_login_scenario(credentials: ImmutableCredentials) -> SeleniumTestScenario:
    def _scenario(driver, logger):
        dashboard_creds = credentials                           # ← closure
        on_dashboard_login_page = DashboardLoginPage(driver=driver)
        on_dashboard_welcome_page = DashboardWelcomePage(driver=driver)
        ...
        return Scenario(test_chain=[
            drive_page(
                ...,
                act(on_dashboard_login_page,
                    login_without_otp_and_with_retries(dashboard_creds, retries_amount, logger=logger))
                    .failure(just_log_error("Failed to connect..."))
                    .success(just_log_success(f"Connected to the dashboard as {dashboard_creds['login']}!")),
            ),
            drive_page(
                act(on_dashboard_welcome_page, ...)...,
            ),
        ])
    return _scenario


multi_login_tests = [
    create_selenium_test(
        name=f"Login - {creds['login']}",
        test_scenario=_create_login_scenario(creds),
    )
    for creds in multi_login_dataset
]
```

- **Factory `_create_login_scenario(creds)`**&nbsp;: retourne un `_scenario` qui capture `creds` via une closure.
- **Liste de tests**&nbsp;: un test par entrée du dataset, nommé `"Login - <login>"`.
- **`Scenario` au lieu d'une simple `test_chain`**&nbsp;: retourné parce qu'on construit dans la factory, on encapsule.

## Suite data-driven

```python
def create_suite(*, drivers_pool: SeleniumWebDriversPool) -> TestSuite:
    return TestSuite(
        name="Login (data-driven PoC)",
        tests=[*multi_login_tests],            # ← unpack
        drivers_pool=drivers_pool,
    )
```

`[*multi_login_tests]` unpacke la liste dans le `tests=`.  
Si on veut ajouter des tests _en plus_&nbsp;: `tests=[*multi_login_tests, test_extra]`.

## Pattern généralisable

Le Holy Book le formalise (chapitre `datasets-smoke-tests-...`):

> Une _closure_ suffit. On notera que `Scenario` est déclaré depuis l'intérieur ici&nbsp;: logique, puisqu'il s'agit de l'encapsuler.

Pattern réutilisable pour tout test où&nbsp;:

1. La _forme_ du scénario est identique.
2. Seules les _données d'entrée_ varient.
