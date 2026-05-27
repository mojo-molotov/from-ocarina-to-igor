---
title: "02.08 — POMBase"
weight: 8
date: 2026-05-20
series: ["ocarina"]
series_order: 8
tags: ["selenium"]
---

# 02.08&nbsp;—&nbsp;`POMBase`

> Source file: [`src/ocarina/pom/base.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/pom/base.py)
>
> **Framework-agnostic** abstract base for the Page Object Model. Two required methods. Zero mention of Selenium.

## Code

```python
class POMBase(ABC):
    @abstractmethod
    def verify(self, *, timeout: float | None = None) -> Self:
        ...

    @abstractmethod
    def get_current_title(self) -> str:
        ...
```

Six bytes of contract (the two signatures). That's all.

## Why two methods

### `verify(timeout=None) -> Self`

Purpose: **prove we're on the right page**. Otherwise, raise.

- `timeout` lets you wait _up to a given time_ for the page to load (handy for Selenium `WebDriverWait`).
- `None` default lets the implementation decide (typically reading `get_timeout()` which reads the CLI).
- Returning `Self` enables fluent _method chaining_ (`MyPage(...).open().verify().click()`).

The only method test-side that's truly needed to guarantee "I'm on the page I want." Everything else (`click_xxx`, `enter_xxx`) is on the subclass.

### `get_current_title() -> str`

Purpose: **retrieve the current page's title**.

Uses:

1. **Logging**: you can write `logger.info(f"Current page: {page.get_current_title()}")`.
2. **Error-page detection** in `act`'s `on_failure` hook (see [`03-railway/05-create-act-hooks.md`](03-railway/05-create-act-hooks.md)). Example from `ocarina-example`:

   ```python
   def failure_hook(pom: TPOM, exc: Exception) -> Fail:
       title = pom.get_current_title()
       if title and ERROR_PAGE_REGEX.match(title.strip()):
           return Fail(error=HttpErrorPageReachedError(f"HTTP error page: {title}"))
       return Fail(error=exc)
   ```

→ The hook _doesn't know_ what a WebDriver is, but knows how to call `get_current_title()`. Right level of abstraction.

## User-side implementation

```python
@final
class Homepage(SeleniumTitleMixin, POMBase):
    def __init__(self, *, driver: WebDriver, url: str = HOMEPAGE_URL) -> None:
        self._driver = driver
        self._URL = url

    def open(self) -> Homepage:
        self._driver.get(self._URL)
        return self

    def verify(self, *, timeout: float | None = None) -> Homepage:
        try:
            if timeout is None:
                timeout = get_timeout()
            WebDriverWait(self._driver, timeout).until(ec.title_is("Welcome to my homepage"))
            WebDriverWait(self._driver, timeout).until(
                ec.text_to_be_present_in_element((By.TAG_NAME, "h1"), "My homepage")
            )
        except TimeoutException as exc:
            raise PageVerificationError from exc
        return self
```

1. **`SeleniumTitleMixin`** provides `get_current_title` so subclasses don't duplicate it (see [`10-infra/05-selenium-adapters.md`](10-infra/05-selenium-adapters.md), `mixins.py`).
2. **`verify` raises `PageVerificationError`**, a framework-specific `Exception` subclass. Lets _transient_errors_ match it.
3. **`return self`** every time&nbsp;—&nbsp;fluent chaining.

## Why framework-agnostic

```python
# Selenium
class LoginPage(POMBase):
    def __init__(self, driver: WebDriver):
        self._driver = driver
    def verify(self, timeout=None) -> Self:
        WebDriverWait(self._driver, timeout or 10).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        return self

# Playwright
class LoginPage(POMBase):
    def __init__(self, page: Page):
        self._page = page
    def verify(self, timeout=None) -> Self:
        self._page.wait_for_selector("#login-form", timeout=timeout)
        return self
```

You can write a `PlaywrightTitleMixin`, a `PuppeteerTitleMixin`, …

## `Self` (PEP 673)

```python
@final
class CorsicamonEnterApiKeyPage(SeleniumTitleMixin, POMBase):
    def enter_api_key(self) -> CorsicamonEnterApiKeyPage:        # naive version
        ...
```

vs

```python
@final
class CorsicamonEnterApiKeyPage(SeleniumTitleMixin, POMBase):
    def enter_api_key(self) -> Self:                              # better
        ...
```

The Holy Book (chapter "First steps", section "Returning `self`") notes:

> Every action method returns `self`. It's a deliberate design choice in Ocarina, to be respected systematically; it enables call chaining and the fluent composition of scenarios.

## `verify` is _not_ a matcher

Explicit distinction in the Holy Book (chapter on scenarios composability, section "match_page"):

> It's also not recommended to disguise a `verify` as a _matcher_: **they are two different tools.**

| Tool                           | Goal                               | On failure                       |
| ------------------------------ | ---------------------------------- | -------------------------------- |
| `verify`                       | Guarantee you're on the right page | Raises (`PageVerificationError`) |
| Matcher (used by `match_page`) | Pick a conditional branch          | Returns `False`                  |

## `__init__`

Convention across the entire ecosystem:

```python
def __init__(self, *, driver: WebDriver, url: str = DEFAULT_URL) -> None:
```

`ocarina-with-ai-example`'s `CLAUDE.md` formalizes it as convention:

> POMs take a single `url: str = <DEFAULT_URL>` parameter, defaulted to the constant. Scenarios construct pages with just `Page(driver=driver)` and pass `url=...` only to override.
