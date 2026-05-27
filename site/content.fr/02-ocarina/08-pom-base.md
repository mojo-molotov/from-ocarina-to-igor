---
title: "02.08 — POMBase"
weight: 8
date: 2026-05-20
series: ["ocarina"]
series_order: 8
tags: ["selenium"]
---

# 02.08&nbsp;—&nbsp;`POMBase`

> Fichier source&nbsp;: [`src/ocarina/pom/base.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/pom/base.py)
>
> Base abstraite **framework-agnostic** du Page Object Model. Deux méthodes obligatoires. Aucune mention de Selenium.

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

Six octets de contrat (les deux signatures). C'est tout.

## Pourquoi deux méthodes

### `verify(timeout=None) -> Self`

But&nbsp;: **prouver qu'on est sur la bonne page**. Sinon, lève.

- L'argument `timeout` permet d'attendre _jusqu'à un certain temps_ que la page se charge (utile pour les Selenium `WebDriverWait`).
- Le default `None` laisse l'implémentation choisir (typiquement, lire depuis `get_timeout()` qui lit la CLI).
- Le retour `Self` permet le _method chaining_ fluide (`MyPage(...).open().verify().click()`).

C'est l'unique méthode dont on a vraiment besoin Test-side pour garantir que «&nbsp;_je suis bien sur la page que je veux_&nbsp;». Toutes les actions (`click_xxx`, `enter_xxx`) sont laissées à la subclass.

### `get_current_title() -> str`

But&nbsp;:&nbsp;**récupérer le titre de la page courante**.

Usages&nbsp;:

1. **Logging**&nbsp;:&nbsp;on peut écrire `logger.info(f"Current page: {page.get_current_title()}")`.
2. **Détection de page d'erreur** dans le hook `on_failure` de `act` (cf. [`03-railway/05-create-act-hooks.md`](03-railway/05-create-act-hooks.md)). Exemple `ocarina-example`&nbsp;:

   ```python
   def failure_hook(pom: TPOM, exc: Exception) -> Fail:
       title = pom.get_current_title()
       if title and ERROR_PAGE_REGEX.match(title.strip()):
           return Fail(error=HttpErrorPageReachedError(f"HTTP error page: {title}"))
       return Fail(error=exc)
   ```

&nbsp;→&nbsp;Le hook _ne sait pas_ ce que c'est qu'un WebDriver, mais il sait appeler `get_current_title()`. C'est le bon niveau d'abstraction.

## Implémentation côté utilisateur

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

1. **`SeleniumTitleMixin`** fournit l'implémentation de `get_current_title` pour ne pas dupliquer (cf. [`10-infra/05-selenium-adapters.md`](10-infra/05-selenium-adapters.md), `mixins.py`).
2. **`verify` lève `PageVerificationError`**, sous-classe d'`Exception` propre au framework. Permet aux _transient_errors_ de matcher.
3. **`return self`** systématique&nbsp;:&nbsp;fluent chaining.

## Pourquoi framework-agnostic

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

On peut écrire un `PlaywrightTitleMixin`, un `PuppeteerTitleMixin`, …

## `Self` (PEP 673)

```python
@final
class CorsicamonEnterApiKeyPage(SeleniumTitleMixin, POMBase):
    def enter_api_key(self) -> CorsicamonEnterApiKeyPage:        # version naïve
        ...
```

vs

```python
@final
class CorsicamonEnterApiKeyPage(SeleniumTitleMixin, POMBase):
    def enter_api_key(self) -> Self:                              # mieux
        ...
```

Le Holy Book (chapitre «&nbsp;_Premiers pas_&nbsp;», section «&nbsp;_Retourner `self`_&nbsp;») le note&nbsp;:

> Chaque méthode d'action retourne `self`. C'est un choix de design volontaire dans Ocarina, à respecter systématiquement, il permet le chaînage des appels et la composition fluide des scénarios.

## `verify` n'est _pas_ un matcher

C'est une distinction explicite dans le Holy Book (chapitre sur la composabilité des scénarios, section «&nbsp;_match_&nbsp;»page\_)&nbsp;:

> Il n'est pas non plus recommandé de déguiser un `verify` en _matcher_&nbsp;: **ce sont deux outils différents.**

| Outil                              | But                                  | Comportement sur échec         |
| ---------------------------------- | ------------------------------------ | ------------------------------ |
| `verify`                           | Garantir qu'on est sur la bonne page | Lève (`PageVerificationError`) |
| Matcher (utilisé par `match_page`) | Choisir une branche conditionnelle   | Renvoie `False`                |

## `__init__`

Convention dans tout l'écosystème&nbsp;:

```python
def __init__(self, *, driver: WebDriver, url: str = DEFAULT_URL) -> None:
```

Le `CLAUDE.md` d'`ocarina-with-ai-example` formalise comme convention&nbsp;:

> POMs take a single `url: str = <DEFAULT_URL>` parameter, defaulted to the constant. Scenarios construct pages with just `Page(driver=driver)` and pass `url=...` only to override.
