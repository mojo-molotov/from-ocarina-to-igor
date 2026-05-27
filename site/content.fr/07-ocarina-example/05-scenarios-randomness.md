---
title: "07.05 — Scénarios randomness (4 levels)"
description: "Quatre niveaux de chaos progressifs. On commence simple, on monte en complexité, on stresse de plus en plus Ocarina."
weight: 5
date: 2026-05-20
series: ["ocarina-example"]
series_order: 5
tags: ["watcher"]
---

# 07.05&nbsp;—&nbsp;Scénarios randomness (4 levels)

> Quatre niveaux de chaos progressifs. On commence simple, on monte en complexité, on stresse de plus en plus Ocarina.

## Campagne

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

| Level | Mécanique exercée                  | Difficulté |
| ----- | ---------------------------------- | ---------- |
| 1     | DSL de base (`drive_page`, `act`)  | facile     |
| 2     | `match_page` /&nbsp;`when`         | moyen      |
| 3     | `HumanizedDriver` + `Watcher`      | difficile  |
| 4     | Walkthrough multi-pages chaotiques | difficile  |

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

Test volontairement _flaky_, exerce le hook `on_failure`.

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

Vérifie juste que la page finit par s'afficher en contenant les informations attendues.

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

1. La page peut rendre `Approved` (70%) ou `Disapproved` (30%).
2. `match_page` branche selon `is_approved` /&nbsp;`is_disapproved`.
3. Chaque branche vérifie le rendu correspondant.

Notes&nbsp;:

- Les _matchers_ (`is_approved`, `is_disapproved`) sont des méthodes du POM `DsedMatchers`, distinctes des `verify` (cf. Holy Book&nbsp;: matcher ≠ verify).
- `match_page` ici est le **`match_page` adapté côté projet** (avec `raised_exceptions=transient_errors`).

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

Pattern identique à DSED. Variante&nbsp;: on _instancie_ des POMs spécifiques dans chaque branche (`MadnessCorsPage`, `MadnessThisIsBastiaPage`), pas un seul POM polymorphe.

## Level 3&nbsp;—&nbsp;Chaotic Form (avec `HumanizedDriver` + `Watcher`)

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

1. **`HumanizedDriver`** wrappe le `driver` Selenium pour simuler une saisie humaine (cf. [`07-humanized-driver.md`](07-humanized-driver.md)).
2. **`wpm=125`** (mots/minute), **`typo_rate=0.14`** (14% de typos), etc.
3. **`watchers=[...]`**&nbsp;: un watcher tourne en _daemon_ pendant le test.
4. **`catch_me_if_you_can_cb`**&nbsp;: détecte les éléments `.catch-me-if-you-can` parasites (cf. [`09-watcher-catch-me.md`](09-watcher-catch-me.md)).
5. **`poll_interval=0.8`**&nbsp;: poll toutes les 800 ms.
6. **`HumanizedDriver` est passé au scénario _au lieu_ du driver**&nbsp;: intercepte tous les `find_element` du POM.

## Level 4&nbsp;—&nbsp;Walkthrough

```python
# tests/scenarios/randomness/level_4/walkthrough.py
def scenario_walkthrough(driver, logger):
    on_homepage = Homepage(driver=driver)
    return [
        drive_page(act(on_homepage, open_homepage)..., act(on_homepage, verify_homepage)...),
        # ... ouverture séquentielle de chaque page de l'Igoristan ...
        # ... vérification de leur titre ...
        # ... retour homepage ...
    ]
```

Un test qui fait un «&nbsp;_tour complet_&nbsp;», une promenade tranquille jusque dans les limbes de l'Igoristan.

## `HumanizedDriver` instancié depuis l'extérieur

```python
test_scenario=lambda driver, logger: Scenario(
    test_chain=_send_chaotic_form(HumanizedDriver(driver, ...), logger),
    ...
)
```

- Le _vrai_ `driver` arrive depuis la pool.
- On le _wrappe_ dans `HumanizedDriver(driver, ...)`.
- On passe le wrapper au scénario.
- Tous les POMs reçoivent le wrapper.

Ici&nbsp;: `pom._driver = humanized_driver`.  
Quand le POM fait `self._driver.find_element(...).send_keys(...)`, c'est le `humanized` qui intercepte et fait la saisie lente avec typos.
