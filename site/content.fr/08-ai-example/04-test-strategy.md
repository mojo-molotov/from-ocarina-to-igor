---
title: "08.04 — Stratégie de test"
description: "Six types de tests, six rôles distincts. Documentés dans CURA_TEST_STRATEGY.md §3."
weight: 4
date: 2026-05-20
series: ["ai-example"]
series_order: 4
tags: ["parallelisation"]
---

# 08.04&nbsp;—&nbsp;Stratégie de test

> Six **types de tests**, six rôles distincts. Documentés dans `CURA_TEST_STRATEGY.md` §3.

## Types de test

| Type                                                                                                                        | Statut attendu                                                      | Source d'autorité                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Happy path** (cas passant)                                                                                                | PASS                                                                | Parcours nominaux décrits d'après les SFD                                                                      |
| **Unhappy path** (cas non passant)                                                                                          | PASS (le test passe quand l'application refuse de "laisser passer") | Validations existantes correctes                                                                               |
| **Edge case /&nbsp;boundary** (tests aux limites)                                                                           | PASS ou FAIL                                                        | Selon le test, souvent accompagné d'une note ajoutée sur les SFD                                               |
| **Business attack /&nbsp;gap test** (tests fonctionnels pour essayer de faire "tomber" le produit et d'identifier des gaps) | **FAIL intentionnel**                                               | Comportements qu'un système devrait empêcher mais que CURA n'empêche pas                                       |
| **Exploratory /&nbsp;observed-behaviour** (exploratoire)                                                                    | PASS                                                                | Documente le comportement actuel quand la spec ne le couvre pas                                                |
| **Permanent security regression fixture** (non-régression)                                                                  | PASS (= la sécurité tient)                                          | Vérifie qu'un correctif de sécurité tient (correctifs qui resteront définitivement dans le patrimoine de test) |

## Happy path

> Exercises the nominal flow with valid inputs and an authenticated user. Verifies that the system produces the correct output (confirmation, history entry, etc.).

`valid_login.py`&nbsp;—&nbsp;connexion avec identifiants valides&nbsp;→&nbsp;on _s'attend_ à une connexion en succès.

## Unhappy path

> Exercises flows where the user provides invalid input or acts outside their authorisation. The test **passes** when the application responds with the correct rejection.

- Connexion avec mauvais identifiants&nbsp;→&nbsp;on _s'attend_ à un message d'erreur.
- Empty creds&nbsp;→&nbsp;on _s'attend_ à un message d'erreur.
- Accès non autorisé à la page d'historique de consultations&nbsp;→&nbsp;on _s'attend_ à une redirection.
- Envoi d'un formulaire de prise de RDV sans avoir précisé la date&nbsp;→&nbsp;on _s'attend_ à ce que l'envoi soit refusé.

## Edge case /&nbsp;boundary

> Exercises the limits of what the application is supposed to accept or reject, where the specification is unclear or the behaviour is surprising.

Synchronisé avec le document de spécifications (`CURA_FRD.md`)&nbsp;: on y ajoute une _note_ quand un gap est trouvé.

## Business attack /&nbsp;gap test

Tests intentionnellement en échec jusqu'à livraison de correctifs&nbsp;:

| Test                                                                 | Gap      | SFD  |
| -------------------------------------------------------------------- | -------- | ---- |
| `Appointment - Server accepts empty date when client bypass applied` | G-DATA-1 | §9.1 |
| `Appointment - Past date booking accepted`                           | G-DATA-1 | §9.7 |
| `Appointments - Duplicate booking`                                   | G-DATA-2 | §9.6 |
| `Appointments - Overlapping appointments`                            | G-DATA-2 | §9.6 |
| `Journey - History ordered most-recent date first`                   | G-SPEC-1 | §9.8 |

> Implementation rule: gap tests must fail with a clear, specific message&nbsp;—&nbsp;not a generic `TimeoutException`. They use `ConfirmationPage.verify_not_confirmed()`, which checks `url_contains("appointment.php")` (fast, not DOM-dependent, not blocked by HTML5 validation popups). The assertion window is fixed at `_NOT_CONFIRMED_TIMEOUT` (10 s, defined in `confirmation.py`) and is intentionally **independent of `--wait-timeout`**.

→ Discipline&nbsp;: un _gap test_ doit échouer **clairement**.

`_NOT_CONFIRMED_TIMEOUT` est fixe (10s) et **délibérément** décorrélé de `--wait-timeout`.  
Si on augmente `--wait-timeout` pour stabiliser un autre test, on ne veut pas risquer de faire accidentellement passer un _gap test_ par effet de bord.

## Distinguer gap test vs validation test

> Distinguishing a gap test from a validation pass:
>
> - **Gap test (intentionally FAILS):** CURA _should_ reject X but doesn't. The test asserts rejection; the failure documents the gap.
> - **Validation test (PASSES):** CURA _does_ correctly reject X. The test asserts rejection; the pass confirms the validation still works.

Deux tests _peuvent avoir des intentions opposées_. Le **nom** du test, la _docstring_ et la **ligne** dans `IDENTIFIED_GAPS.md` sont là pour les distinguer.

## Exploratory /&nbsp;observed-behaviour

> Documents what CURA actually does when no requirement is specified. These tests **pass** and record the observed behaviour both in the per-test log and in the SFD.

`saturation_booking.py`&nbsp;—&nbsp;5 réservations consécutives sur des dates différentes en une session, toutes acceptées. Documente l'absence de rate limit.

> When to add one:
>
> - A business-logic constraint is plausible but absent from the SFD ("can I book the same date twice in different slots?").
> - Decide before writing: is the current behaviour reasonable (→ exploratory /&nbsp;pass) or a gap (→ assertive /&nbsp;intentional fail)?
> - Always pair with an SFD update.

→ Décision _humaine_ avant l'écriture&nbsp;: OK ou gap&nbsp;?

1. Si OK&nbsp;: test exploratoire en succès.
2. Si gap&nbsp;: test assertif destiné à être intentionnellement en échec.

## Tests de régression persistants

Vérifie qu'un correctif de sécurité (donc correctif critique) tient.  
Si un jour le correctif casse&nbsp;: ce test s'allume à nouveau en rouge. Documente le _maintien_ de la correction.

## `cycles/e2e.py`

```python
E2E_CYCLE_NAME = "CURA E2E"

def create_e2e_test_cycle(drivers_pool) -> TestCycle[WebDriver]:
    return TestCycle(
        name=E2E_CYCLE_NAME,
        smoke_tests_campaigns=[create_prerequisites_campaign(drivers_pool=drivers_pool)],
        campaigns=[
            create_authentication_campaign(drivers_pool=drivers_pool),
            create_appointments_campaign(drivers_pool=drivers_pool),
            create_profile_campaign(drivers_pool=drivers_pool),
            create_user_journeys_campaign(drivers_pool=drivers_pool),
        ],
    )
```

## Hiérarchie

```
Cycle "CURA E2E"
├── Smoke (gate, fail-fast)
│   └── Campaign "Prerequisites"
│       └── Suite "Authentication baseline"
│           └── Test "valid_login"                     # gate
│
└── Main
    ├── Campaign "Authentication"
    │   ├── Suite "Session management"
    │   └── Suite "Failure modes"
    │       ├── failed_logins.py                       # data-driven : invalid / empty / wrong-case
    │       ├── unauthenticated_appointment_access.py
    │       ├── unauthenticated_history_access.py
    │       ├── unauthenticated_profile_access.py
    │       ├── logout.py
    │       ├── post_logout_access.py
    │       ├── post_logout_bfcache_exposure.py        # B-BROWSER-1
    │       ├── post_logout_frenetic_navigation.py
    │       ├── post_logout_server_invalidation.py
    │       └── rapid_logout_relogin.py
    ├── Campaign "Appointments"
    │   ├── Suite "Booking"
    │   │   ├── book_appointments.py                   # data-driven : Hongkong / Tokyo+readmission / Seoul
    │   │   ├── missing_visit_date_validation.py
    │   │   ├── server_side_date_bypass.py             # G-DATA-1
    │   │   ├── past_date_booking.py                   # G-DATA-1
    │   │   ├── enter_on_visit_date_no_submit.py
    │   │   ├── duplicate_booking.py                   # G-DATA-2
    │   │   ├── overlapping_appointments.py            # G-DATA-2
    │   │   └── saturation_booking.py                  # exploratory
    │   └── Suite "History"
    │       ├── view_history.py
    │       └── empty_history.py
    ├── Campaign "Profile"
    │   └── Suite "Profile access"
    │       └── view_profile.py                        # G-SPEC-2 documente la placeholder
    └── Campaign "User journeys"
        └── Suite "Cross-feature flows"
            ├── book_and_verify_history.py
            ├── history_ordering.py                    # G-SPEC-1
            ├── sidebar_navigation.py
            └── sidebar_login_navigation.py
```

## `CLAUDE.md`

### «&nbsp;_Smoke is structural, not lexical_&nbsp;»

> Express the gate via `TestCycle.smoke_tests_campaigns=`; never put "smoke" in a name string.

→ Le mot «&nbsp;_smoke_&nbsp;» ne doit pas apparaître dans les noms de tests /&nbsp;suites. La sémantique est portée par la **structure** Ocarina (`smoke_tests_campaigns=`), pas par un nom.

### «&nbsp;_Smoke is the minimum that proves the system is alive_&nbsp;»

> A test belongs in smoke iff its failure makes the rest of the cycle uninformative.

→ Critère strict&nbsp;: un test n'est dans le groupe des smoke tests que si son échec _invalide_ le reste.  
Comme `valid_login`&nbsp;: sans pouvoir s'authentifier, on ne peut rien tester sur CURA.

### «&nbsp;_Each main campaign is feature-shaped, not method-shaped_&nbsp;»

→ Campagnes nommées par fonctionnalités (`Authentication`, `Appointments`, `Profile`, `User journeys`), pas par méthode (`POST tests`, `GET tests`).

### «&nbsp;_Default mode is fail-fast_&nbsp;»

→ Le mode par défaut des smoke tests suffit pour ce cycle de test. `wait-for-all-smoke-tests` est réservé aux cas où plusieurs smoke tests sont **indépendants** (cf. `ocarina-example` qui a 2 smoke campaigns).

## `--workers 3`

> **Never `--workers 1`.** Single-worker runs mask concurrency failures and diverge from CI. Always `--workers 3` (matches `ai_proof_e2e.yml`); CI is the canonical reference.

→ Discipline&nbsp;: ne **jamais** tester en _single-worker_.

1. Un seul worker masque les races conditions.
2. La CI tourne avec 3 workers&nbsp;; on veut faire la même chose en local.
3. `saturate_workers=True` clone les tests pour atteindre N = 3&nbsp;→&nbsp;exposition aux _heisenbugs_.
