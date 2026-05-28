---
title: "08.06 — Gaps data (G-DATA-1, G-DATA-2)"
description: "Les deux gaps d'intégrité des données de CURA, dont l'absence de validation serveur de la date de visite, documentés par ocarina-with-ai-example."
weight: 6
date: 2026-05-20
series: ["ai-example"]
series_order: 6
---

# 08.06&nbsp;—&nbsp;Gaps data (G-DATA-1, G-DATA-2)

> Deux gaps majeurs sur l'intégrité des données.

## G-DATA-1&nbsp;—&nbsp;Pas de validation serveur de `visit_date`

### Source

```php
// appointment.php
array_diff_key($_POST, array(
    "facility" => "",
    "hospital_readmission" => "",
    "programs" => "",
    "visit_date" => "",
    "comment" => ""
))
```

Cette ligne fait juste une vérification de _présence des clés_.  
Elle ne valide **jamais** la valeur de `visit_date`.

### Symptôme

1. **Empty visit_date**&nbsp;: si on supprime l'attribut HTML5 `required` via JS et qu'on submit avec une date vide&nbsp;→&nbsp;prise de RDV acceptée.
2. **Past visit_date**&nbsp;:&nbsp;si on envoie une réservation antidatée&nbsp;→&nbsp;prise de RDV acceptée.
3. La réservation est bien ajoutée à l'historique telle quelle.

### Tests associés

| Test                                                                 | Manière                                                                                                                     |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `Appointment - Server accepts empty date when client bypass applied` | Retire l'attribut `required`, envoie avec date de réservation vide&nbsp;→&nbsp;s'attend à être rejeté par le système (FAIL) |
| `Appointment - Past date booking accepted`                           | Envoie une demande de RDV pour hier&nbsp;→&nbsp;s'attend à être rejeté par le système (FAIL)                                |

Les deux tests **sont intentionnellement en échec**.  
Ils documentent le gap.

### «&nbsp;_Past date booking_&nbsp;»

```python
# src/tests/scenarios/appointment/past_date_booking.py
"""Past-date booking accepted — no temporal validation (§9.7 gap).

Flow:
  open appointment form → fill (facility, program, comment, date = yesterday) → submit
  → verify NOT confirmed
  (intentional FAIL — CURA accepts past dates, §9.7 gap)

A healthcare scheduling system must not accept bookings for dates that have
already passed. CURA performs no temporal validation: yesterday's date is
accepted and a confirmation is returned. The test asserts rejection and fails
when the confirmation appears.

Pre-fragments: login_as_demo_user
Post-fragments: (none)
"""

def _scenario_past_date_booking(driver, logger) -> TestChain:
    on_appointment = AppointmentPage(driver=driver)
    on_confirmation = ConfirmationPage(driver=driver)

    log_error = create_just_log_error(logger=logger)
    log_success = create_just_log_success(logger=logger)
    log_and_screenshot = create_log_success_and_take_screenshot(driver=driver, logger=logger)

    return [
        drive_page(
            act(on_appointment, open_appointment_page)
                .failure(log_error("Failed to open appointment form"))
                .success(log_success("Opened appointment form")),
            act(on_appointment, fill_appointment(
                facility="Hongkong CURA Healthcare Center",
                programs="Medicare",
                visit_date=in_days(-1),                    # ← hier
                comment="Past-date booking attempt",
            ))
                .failure(log_error("Failed to fill form"))
                .success(log_and_screenshot("Filled form with past date")),
            act(on_appointment, submit_appointment)
                .failure(log_error("Failed to submit"))
                .success(log_success("Submitted")),
        ),
        drive_page(
            act(on_confirmation, verify_booking_not_confirmed)
                .failure(log_error("CURA accepted past date — §9.7 gap"))
                .success(log_and_screenshot("Rejection confirmed")),
        ),
    ]
```

- `verify_booking_not_confirmed` retourne success si on est _resté_ sur `/appointment.php` (= rejet).
- Si on a été redirigé vers `/confirmation.php` (= acceptation), `verify_booking_not_confirmed` lève&nbsp;→&nbsp;`.failure()` log explicite «&nbsp;_CURA accepted past date&nbsp;—&nbsp;§9.7 gap_&nbsp;».

### `verify_booking_not_confirmed`

```python
# pages/confirmation.py
_NOT_CONFIRMED_TIMEOUT = 10                    # ← fixe, indépendant de --wait-timeout

class ConfirmationPage(...):
    def verify_booking_not_confirmed(self) -> ConfirmationPage:
        try:
            WebDriverWait(self._driver, _NOT_CONFIRMED_TIMEOUT).until(
                ec.url_contains("appointment.php")
            )
            return self                          # ✅ on est resté sur appointment → rejet
        except TimeoutException as exc:
            raise BookingNotRejectedError(
                f"CURA accepted the booking (url: {self._driver.current_url}); §9.7 gap"
            ) from exc
```

1. **`url_contains("appointment.php")`**&nbsp;: test sur URL, pas sur le DOM (choix d'implémentation correspondant au comportement de CURA).
2. **`_NOT_CONFIRMED_TIMEOUT = 10`**&nbsp;: fixe à 10s, _indépendant de `--wait-timeout`_.
3. **`BookingNotRejectedError`**&nbsp;: exception _spécifique_. Pas un `AssertionError`. Pas un `TimeoutException`. Ce N'EST PAS un _flake_.

## G-DATA-2&nbsp;—&nbsp;Pas de contrainte d'unicité ni de vérification de conflit

### Source

```php
// appointment.php
array_push($_SESSION['history'], $_POST);
```

`array_push` _inconditionnel_.

Aucune vérification&nbsp;:

1. Pas de check&nbsp;: «&nbsp;_cet utilisateur a-t-il déjà un RDV pour cette date&nbsp;?_&nbsp;».
2. Pas de check&nbsp;: «&nbsp;_ces deux RDV sont-ils géographiquement compatibles&nbsp;?_&nbsp;» (Hongkong + Tokyo le même jour, au même nom).

### Symptômes

- **Duplicate**&nbsp;: deux RDV identiques&nbsp;→&nbsp;les deux sont pris et apparaissent dans l'historique.
- **Overlap**&nbsp;: deux RDV le même jour mais à des lieux très éloignés (Hongkong + Tokyo)&nbsp;→&nbsp;les deux sont pris.

### Tests associés

| Test                                      | Manière                                               | FAIL&nbsp;?         |
| ----------------------------------------- | ----------------------------------------------------- | ------------------- |
| `Appointments - Duplicate booking`        | Réserve A, puis réserve A encore                      | FAIL (CURA accepte) |
| `Appointments - Overlapping appointments` | Réserve Hongkong/2025-05-18, réserve Tokyo/2025-05-18 | FAIL (CURA accepte) |

`book_then_verify_not_confirmed`

Pour ces tests, on _re-utilise_ le pattern G-DATA-1&nbsp;:

1. Réserve un premier RDV (accepté).
2. Réserve un second insensé (devrait être rejeté).
3. `verify_booking_not_confirmed` sur le second.

Si le second RDV est accepté aussi&nbsp;→&nbsp;fail (gap confirmé).

`_NOT_CONFIRMED_TIMEOUT`

Tous ces gap tests utilisent cette constante&nbsp;:

```python
_NOT_CONFIRMED_TIMEOUT = 10
```

C'est un constante qui _contourne sciemment les paramètres CLI_. Si quelqu'un augmente `--wait-timeout` à 30 pour stabiliser un autre test, les gap tests restent à 10.

Pas de risque de **gonfler silencieusement** la fenêtre de gap.

`CURA_TEST_STRATEGY.md`&nbsp;:

> The assertion window is fixed at `_NOT_CONFIRMED_TIMEOUT` (10 s, defined in `confirmation.py`) and is intentionally **independent of `--wait-timeout`**: bumping the global wait flag for driver stability must not silently inflate every gap test's assertion budget.

## `saturation_booking`

> Example: `saturation_booking.py`&nbsp;—&nbsp;5 consecutive bookings on different dates in one session, all accepted; documents the absence of a rate limit.

C'est un test _exploratoire_ (pas un gap test). Il **passe** parce qu'il documente le comportement actuel (CURA accepte 5 prises de RDV rapides). Si CURA un jour ajoutait un rate-limit qui rejette le 5e, ce test casserait&nbsp;→&nbsp;on _réviserait_ le test pour refléter la nouvelle réalité.

## Pédagogie

| Concept                                                                                                   | Test                                            |
| --------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Comment exprimer un gap test                                                                              | `past_date_booking.py`                          |
| Comment gérer un timeout indépendant                                                                      | `_NOT_CONFIRMED_TIMEOUT`                        |
| Comment distinguer une exception «&nbsp;_SUT défaillant_&nbsp;» d'un «&nbsp;_comportement attendu_&nbsp;» | `BookingNotRejectedError` vs `TimeoutException` |
| Comment documenter un comportement observé sans gap assertion                                             | `saturation_booking.py`                         |
