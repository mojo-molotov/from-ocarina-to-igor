---
title: "03.05 — Programmation déclarative"
description: "Un scénario d'Ocarina décrit, il n'exécute pas. C'est ce qui le rend factorisable, multipliable, et lisible."
weight: 5
date: 2026-05-20
series: ["fonctionnel"]
series_order: 5
tags: ["scenarios"]
---

# 03.05&nbsp;—&nbsp;Programmation déclarative

> Un scénario d'Ocarina **décrit**, il n'exécute pas. C'est ce qui le rend factorisable, multipliable, et lisible.

## Démonstration

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

Ce code **n'exécute rien**. Il **décrit**&nbsp;:

- «&nbsp;_je prends le contrôle de la homepage_&nbsp;»,
- «&nbsp;_j'ouvre + vérifie&nbsp;; sur erreur log A, sur succès log B_&nbsp;»,
- «&nbsp;_je clique sur le CTA&nbsp;; sur erreur log C, sur succès log D_&nbsp;»,
- «&nbsp;_je prends le contrôle de la page suivante_&nbsp;»,
- «&nbsp;_j'y vérifie&nbsp;; logs_&nbsp;».

Le Holy Book le formule explicitement&nbsp;:

> Cette écriture est pure, elle ne provoque aucun _effet_ immédiat.
> Tout peut être redéclaré ailleurs, réorganisé ailleurs, tant que la chaîne finale correspond à l'attendu.

## Capacités qui découlent du déclaratif

### 1. Aliasing

```python
click_confirm_cookies = drive_page(
    act(on_homepage, confirm_cookie_banner)
        .failure(log_error_with_current_url("Failed..."))
        .success(log_success_with_current_url_and_take_screenshot("Confirmed!"))
)

# … plus tard …
[
    match_page(branches=[
        when(check.has_cookies_banner, name="cookies", then=[click_confirm_cookies]),
        when(check.has_not_cookies_banner, name="no cookies", then=[]),
    ]),
    drive_page(...),
]
```

→ On extrait un `drive_page` dans une variable, on le réutilise. C'est juste une valeur.

### 2. Multiplication

```python
[
    drive_page(
        act(on_dashboard, click_btn)...,
        act(on_dashboard, verify_msg)...,
    ),
] * 5
```

→ Reproduit la chaîne 5 fois. Sans paresse, on exécuterait une fois et on aurait 5 références au même résultat&nbsp;; avec, on a 5 exécutions distinctes.

### 3. Fragments

```python
test_with_fragments = create_selenium_test(
    name="...",
    test_scenario=lambda driver, logger: Scenario(test_chain=my_chain(driver, logger)),
    pre_test_scenarios_fragments=[login_without_otp_happy_path],     # ← fragment injecté avant
    post_test_scenarios_fragments=[verify_homepage],                 # ← fragment injecté après
)
```

→ Les fragments sont **concaténés** par `Test.spawn`.

### 4. Data-driven

```python
multi_login_dataset = [
    MappingProxyType({"login": "any", "password": "figatellu"}),
    MappingProxyType({"login": "Napoleon", "password": "figatellu"}),
    ...
]

def _create_login_scenario(credentials):
    def _scenario(driver, logger):
        # closure capturant credentials
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

→ Un dataset de credentials&nbsp;→&nbsp;une liste de tests. La _factory_ `_create_login_scenario` est appliquée à chaque entrée. C'est de la composition `dataset × scenario_template = tests`.

### 5. Branchement sans état

```python
[
    match_page(branches=[
        when(check.has_cookies_banner, name="cookies", then=[click_confirm_cookies]),
        when(check.has_not_cookies_banner, name="no cookies", then=[]),
    ]),
    drive_page(act(on_homepage, do_next_thing)...),
]
```

→ La branche est sélectionnée au _runtime_, mais la structure du scénario est déclarée à l'avance.

## La distinction impératif vs déclaratif appliquée

Le Holy Book le mentionne (chapitre «&nbsp;_Premiers retours_&nbsp;»)&nbsp;:

> _M'expliquer ce que sont la programmation impérative et déclarative en racontant n'importe quoi_

| Impératif                                 | Déclaratif                                      |
| ----------------------------------------- | ----------------------------------------------- |
| Suite d'instructions avec mutation d'état | Description de _ce qu'on veut_                  |
| Le programme _fait_ des choses            | Le programme _est_ une description              |
| Difficile à composer /&nbsp;reorder       | Facile à composer /&nbsp;reorder                |
| Tests fragiles aux side-effects           | Tests robustes (le test exécute la description) |

Le DSL d'Ocarina est strictement déclaratif au niveau scénario. L'exécution est **un événement séparé** (`runner.run()` ou `chain_runner.run()` appelés par `TestExecutor`).

Également tiré du Holy Book (chapitre sur la composabilité des scénarios)&nbsp;:

> **La priorité des scénarios de test est leur uniformité et leur simplicité. C'est tout.**

On **n'imbrique pas** des `try/except` dans un scénario, on **ne stocke pas** d'état entre les `act`, on **ne** définit pas de fonction `helper_step()` qui fait plein de choses. La grammaire DSL impose la déclaration.

## Lien avec l'IA

Cette propriété est centrale pour la collaboration IA&nbsp;:

> _Avec l'IA, et des outils comme Claude Code, ce pari devient chaque jour plus solide. Le pont entre techniques et non-techniques n'est plus une couche d'abstraction._
>
> _C'est l'IA elle-même. IA qui travaille sur de la donnée brute._

Un scénario déclaratif est de la _donnée brute_ (au sens où il décrit, sans logique cachée). C'est ce que l'IA consomme et produit le mieux.

C'est aussi pourquoi tout le système (`mypy strict`, `ruff ALL`, `pytest-mypy-plugins`) maximise les tests statiques, typage statique compris&nbsp;: autant pour les humains que pour les LLMs.
