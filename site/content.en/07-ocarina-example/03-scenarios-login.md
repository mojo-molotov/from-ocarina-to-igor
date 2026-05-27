---
title: "07.03 — Dashboard login scenarios"
description: "Three families: happy paths, unhappy paths, data-driven multi-login. All exercise the 10%-fail useAuth and OTP coordination."
weight: 3
date: 2026-05-20
series: ["ocarina-example"]
series_order: 3
tags: ["scenarios", "otp"]
---

# 07.03&nbsp;—&nbsp;Dashboard login scenarios

> Three families: happy paths, unhappy paths, data-driven multi-login. All exercise the 10%-fail `useAuth` and OTP coordination.

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

### Test 1: login without OTP

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

1. **`retries_amount = max(get_max_workers(), 10)`**: at least 10 internal login retries to beat the 10% random failure.
2. **`login_without_otp_and_with_retries(creds, retries_amount, logger=logger)`**: closure capturing creds, retry count, and logger. Returns `Callable[[DashboardLoginPage], DashboardLoginPage]`.
3. **2 `drive_page`s**: login page then welcome page. Each opens, verifies, screenshots.
4. **Log factories everywhere**: no inline lambdas.
5. **`SeleniumTitleMixin`**: `get_current_title()` feeds `act`'s `on_failure` hook.

### Test 2: login with OTP

```python
def dashboard_login_with_otp_happy_path(driver, logger):
    # ... same setup ...

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

Three `drive_page`s, five `act`s in the first. L1 cache + reserved keys share values between acts (see [`08-caches-locks.md`](08-caches-locks.md)).

### Test 3: back to Igoristan button

Click "Back to Igoristan" on the login page, verify we're back on the homepage. Uses `post_test_scenarios_fragments=[verify_homepage]`.

## Unhappy paths

`tests/scenarios/dashboard/access/unhappy_paths.py`

- Login with wrong password → error displayed.
- Access to `/dashboard/nested` _without_ login → redirect.
- Access to `/dashboard/nested` _with_ login _without_ OTP → "_Access requires OTP_" message.

The 3rd case uses `pre_test_scenarios_fragments=[login_without_otp_happy_path]`:

```python
test_cant_access_the_protected_page_without_otp_using_the_ui = create_selenium_test(
    name="Can't access the protected page without OTP (using the UI)",
    test_scenario=lambda driver, logger: Scenario(
        test_chain=dashboard_access_to_protected_page_without_otp_using_the_ui(driver, logger)
    ),
    pre_test_scenarios_fragments=[login_without_otp_happy_path],
)
```

The fragment `login_without_otp_happy_path` runs before the test&nbsp;—&nbsp;so the test starts already logged in without OTP.

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

Five logins, all valid (`figatellu` is a master password). Each entry generates one test:

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

- **`_create_login_scenario(creds)` factory**: returns a `_scenario` that captures `creds` in a closure.
- **One test per dataset entry**, named `"Login - <login>"`.
- **`Scenario` wrapping the `test_chain`**: built inside the factory so it's self-contained.

## Data-driven suite

```python
def create_suite(*, drivers_pool: SeleniumWebDriversPool) -> TestSuite:
    return TestSuite(
        name="Login (data-driven PoC)",
        tests=[*multi_login_tests],            # ← unpack
        drivers_pool=drivers_pool,
    )
```

`[*multi_login_tests]` unpacks the list into `tests=`. To add extra tests: `tests=[*multi_login_tests, test_extra]`.

## Generalizable pattern

The Holy Book formalizes it (chapter "First jutsus"):

> A _closure_ is all it takes.  
> Note that `Scenario` is declared from the inside here. It makes sense, since the whole point is to encapsulate it.

Reusable for any test where the scenario shape is identical and only the input data varies.
