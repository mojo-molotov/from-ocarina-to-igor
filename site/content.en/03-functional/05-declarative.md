---
title: "03.05 — Declarative programming"
description: "An Ocarina scenario describes, it doesn't execute. That's what makes it factorable, multipliable, readable."
weight: 5
date: 2026-05-20
series: ["functional"]
series_order: 5
tags: ["scenarios"]
---

# 03.05&nbsp;—&nbsp;Declarative programming

> An Ocarina scenario **describes**, it doesn't execute. That's what makes it factorable, multipliable, readable.

## Demonstration

```python
return [
    drive_page(
        act(on_homepage, open_then_verify_homepage)
            .failure(just_log_error("Failed to reach the homepage..."))
            .success(log_success_with_current_url_and_take_screenshot("On the homepage!")),
        act(on_homepage, click_book_call_page_cta)
            .failure(just_log_error("Failed to click on the 'Book a call' CTA..."))
            .success(just_log_success("Clicked on the 'Book a call' CTA!")),
    ),
    drive_page(
        act(on_book_a_call_page, verify_book_call_page)
            .failure(just_log_error("Failed to verify the 'Book a call' page..."))
            .success(log_success_with_current_url_and_take_screenshot("On the 'Book a call' page!")),
    ),
]
```

This code **executes nothing**. It **describes**:

- "_I take control of the homepage_",
- "_I open + verify; on error log A, on success log B_",
- "_I click the CTA; on error log C, on success log D_",
- "_I take control of the next page_",
- "_I verify it; logs_".

The Holy Book puts it explicitly (chapter "First scenarios"):

> This style of writing is pure: it produces no immediate _effect_.
> Everything can be redeclared elsewhere, reorganized elsewhere, as long as the final chain matches what is expected.

## Capabilities that flow from declarativity

### 1. Aliasing

```python
click_confirm_cookies = drive_page(
    act(on_homepage, confirm_cookie_banner)
        .failure(log_error_with_current_url("Failed..."))
        .success(log_success_with_current_url_and_take_screenshot("Confirmed!"))
)

# … later …
[
    match_page(branches=[
        when(check.has_cookies_banner, name="cookies", then=[click_confirm_cookies]),
        when(check.has_not_cookies_banner, name="no cookies", then=[]),
    ]),
    drive_page(...),
]
```

→ We pull a `drive_page` into a variable and reuse it. Just a value.

### 2. Multiplication

```python
[
    drive_page(
        act(on_dashboard, click_btn)...,
        act(on_dashboard, verify_msg)...,
    ),
] * 5
```

→ Repeats the chain 5 times. Without laziness, we'd execute once and hold 5 refs to the same result; with it, we get 5 distinct executions.

### 3. Fragments

```python
test_with_fragments = create_selenium_test(
    name="...",
    test_scenario=lambda driver, logger: Scenario(test_chain=my_chain(driver, logger)),
    pre_test_scenarios_fragments=[login_without_otp_happy_path],     # ← fragment injected before
    post_test_scenarios_fragments=[verify_homepage],                 # ← fragment injected after
)
```

→ Fragments are **concatenated** by `Test.spawn`.

### 4. Data-driven

```python
multi_login_dataset = [
    MappingProxyType({"login": "any", "password": "figatellu"}),
    MappingProxyType({"login": "Napoleon", "password": "figatellu"}),
    ...
]

def _create_login_scenario(credentials):
    def _scenario(driver, logger):
        # closure capturing credentials
        return Scenario(test_chain=[
            drive_page(
                act(page, login_with(credentials))...
            ),
        ])
    return _scenario

multi_login_tests = [
    create_selenium_test(name=f"Login - {c['login']}", test_scenario=_create_login_scenario(c))
    for c in multi_login_dataset
]
```

→ Credentials dataset → list of tests. The `_create_login_scenario` _factory_ applies to each entry. `dataset × scenario_template = tests` composition.

### 5. Stateless branching

```python
[
    match_page(branches=[
        when(check.has_cookies_banner, name="cookies", then=[click_confirm_cookies]),
        when(check.has_not_cookies_banner, name="no cookies", then=[]),
    ]),
    drive_page(act(on_homepage, do_next_thing)...),
]
```

→ Branch picked at _runtime_, scenario's shape declared up front.

## The imperative vs declarative distinction, applied

The Holy Book mentions it (chapter "First feedbacks"):

> _"Explaining" imperative vs. declarative programming to me while spewing complete nonsense_

| Imperative                                   | Declarative                                      |
| -------------------------------------------- | ------------------------------------------------ |
| Sequence of instructions with state mutation | Description of _what you want_                   |
| The program _does_ things                    | The program _is_ a description                   |
| Hard to compose / reorder                    | Easy to compose / reorder                        |
| Tests brittle to side effects                | Robust tests (the test executes the description) |

Ocarina's DSL is strictly declarative at the scenario level. Execution is **a separate event** (`runner.run()` or `chain_runner.run()` called by `TestExecutor`).

Also from the Holy Book (chapter "First scenarios"):

> **The priority of test scenarios is their uniformity and simplicity. That's all.**

You **don't nest** `try/except` in a scenario. You **don't store** state between `act`s. You **don't** define a `helper_step()` that does a bunch of things. The DSL grammar enforces declaration.

## Link with AI

This property is central to AI collaboration. The Holy Book (chapter "First feedbacks") keeps coming back to the same line:

> Code is raw data. Auditable. Inspectable. **A white box.** Exactly what AI has known how to work with since its very beginnings.

A declarative scenario is _raw data_&nbsp;—&nbsp;it describes, no hidden logic. That's what AI consumes and produces best.

Same reason the whole system (`mypy strict`, `ruff ALL`, `pytest-mypy-plugins`) maxes out static checks, including static typing: as much for humans as for LLMs.
