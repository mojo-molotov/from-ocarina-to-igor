---
title: "08.07 — Gaps spec (G-SPEC-1 à G-SPEC-3)"
description: "Les trois gaps de spec de CURA, écarts entre le comportement métier observé et celui attendu d'un système de santé, par ocarina-with-ai-example."
weight: 7
date: 2026-05-20
series: ["ai-example"]
series_order: 7
---

# 08.07&nbsp;—&nbsp;Gaps spec (G-SPEC-1 à G-SPEC-3)

> Trois gaps sur le comportement métier vs la spec _attendue_ d'un système de santé.

## G-SPEC-1&nbsp;—&nbsp;History trié par ordre de soumission, pas par date

### Source

```php
// views/page_history.php
foreach ($_SESSION['history'] as $appointment) {
    // ... render ...
}
```

Pas de `usort`. Pas de tri. Aucune étape de tri n'existe nulle part.

`appointment.php` push avec `array_push($_SESSION['history'], $_POST)`&nbsp;—&nbsp;append en queue (c'est un _pushback_).

### Spec non-respectée

`REQ-HIST-3` des SFD&nbsp;:

> Most recent calendar date first

(Spec _reconstruite_ par l'IA&nbsp;—&nbsp;typique d'un système d'historique.)

### Symptôme

Les RDV apparaissent dans leur ordre de confirmation par le système, indépendamment de `visit_date`. Une demande de RDV pour le 2026-12-31, envoyée aujourd'hui (2026-05-22), et une demande de RDV pour la semaine prochaine, envoyée trois jours plus tard (2026-05-25) finissent affichées avec le RDV pour décembre _au-dessus_ du rendez-vous pour la semaine prochaine.

### Test

```python
# src/tests/scenarios/journey/history_ordering.py
"""History ordered most-recent calendar date first (REQ-HIST-3 / §9.8 gap).

Flow:
  login → book #1 (visit_date = in 30 days) → book #2 (visit_date = tomorrow)
  → open history → verify card order: #2 above #1 (most recent first)
  (intentional FAIL — CURA renders in submission order, §9.8 gap)

Pre-fragments: login_as_demo_user
Post-fragments: (none)
"""
```

→ Test **intentionnellement en échec**. booking#1 (date lointaine) puis booking#2 (date proche) devrait rendre avec #2 affiché en premier dans le listing. CURA les affiche selon leur ordre d'insertion (donc, ici, #1 en haut). Échec documenté.

## G-SPEC-2&nbsp;—&nbsp;Page de profil = placeholder

### Source

```php
// views/page_profile.php
// renders the #profile section but contains no editable fields,
// no form, no API endpoint.
```

### Symptôme

Les users loggés voient «&nbsp;_Profile_&nbsp;» dans le menu, naviguent pour aller dessus, et trouvent **une page vide**. Pas de formulaire, pas de bouton, juste un texte (_placeholder_).

### Test

```python
# src/tests/scenarios/profile/view_profile.py
def scenario_view_profile(driver, logger):
    on_profile = ProfilePage(driver=driver)
    return [
        drive_page(
            act(on_profile, open_profile_page)...,
            act(on_profile, verify_profile_is_placeholder)...,    # PASS = documente le placeholder
        ),
    ]
```

Ce test **PASSE**. Il _documente_ le comportement actuel.  
Ce n'est pas un gap test au sens «&nbsp;_échec intentionnel_&nbsp;»&nbsp;; c'est une trace d'un _test exploratoire_.

Si CURA un jour ajoute une vraie page de profil, `verify_profile_is_placeholder` casserait et on _réviserait_ le test pour vérifier la nouvelle page.

## G-SPEC-3&nbsp;—&nbsp;Un accès non autorisé redirige vers `/`, pas vers la page de connexion

### Source

```php
// appointment.php
if (!$session_check) {
    header("Location: " . SITE_URL);                  // ← redirige vers /
    exit;
}
```

`history.php` fait pareil.

### Spec attendue

Un système devrait rediriger vers `/profile.php#login` (la page de connexion), pas vers `/` (la page d'accueil).  
Sinon l'utilisateur perd le contexte («&nbsp;_je voulais accéder à mon historique_&nbsp;»). C'est un _défaut d'ergonomie_.

### Symptôme

User non-authentifié clique sur un _deep-link_ qui le dirige vers `/appointment.php` ou `/history.php`&nbsp;→&nbsp;il atterit sur la page d'accueil&nbsp;→&nbsp;il doit alors cliquer sur «&nbsp;_Make Appointment_&nbsp;» à nouveau pour atteindre la page de connexion.

### Test

```python
# src/tests/scenarios/login/unauthenticated_appointment_access.py
def scenario_unauthenticated_appointment_access(driver, logger):
    on_appointment = AppointmentPage(driver=driver)
    on_home = HomePage(driver=driver)
    return [
        drive_page(
            act(on_appointment, open_appointment_page)...,
            act(on_appointment, verify_redirected_to_home)...,    # PASS = documente le comportement
        ),
        drive_page(
            act(on_home, verify_home_page)...,
        ),
    ]
```

`unauthenticated_appointment_access.py`, `unauthenticated_history_access.py`, `unauthenticated_profile_access.py`.

Tous ces tests PASSENT, ils _documentent_ de l'exploration.  
Ici, la SFD étant reconstituée et ne faisant pas foi, on ne peut qualifier ce comportement comme étant une _anomalie_ flagrante. On ne peut que _formuler une préconisation et documenter_.

## Pattern&nbsp;: gap test vs exploratory pass

Les gaps spec sont en grande partie _exploratory pass_ (le test passe parce qu'il documente le comportement actuel) plutôt que _intentional fail_ (le test fail parce qu'il assert un blocage qui devrait arriver mais que le système n'impose pas).

| G-DATA-\*                                            | G-SPEC-\*                                                    |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| «&nbsp;_CURA accepte X qu'il devrait rejeter_&nbsp;» | «&nbsp;_CURA fait X au lieu de faire Y_&nbsp;»               |
| Gap test&nbsp;: assert rejection, fail intentionnel  | Test documentaire&nbsp;: assert le comportement actuel, pass |

Les gap tests «&nbsp;_assertive_&nbsp;» sont réservés aux cas où **pour tel parcours utilisateur, un système de santé devrait clairement l'envoyer bouler**. Pour les divergences de spec mineures (ordre de l'historique, page de profil en construction, page de redirection qui pourrait être mieux choisie sans que ce ne soit critique), on _documente_ plutôt qu'on _assert_.

## L'art de choisir

`CURA_TEST_STRATEGY.md`&nbsp;:

> When to add one [exploratory test]:
>
> - A business-logic constraint is plausible but absent from the SFD ("can I book the same date twice in different slots?").
> - **Decide before writing**: is the current behaviour reasonable (→ exploratory /&nbsp;pass) or a gap (→ assertive /&nbsp;intentional fail)?
> - Always pair with an SFD update.

Décision **humaine** avant l'écriture. Pas de bascule automatique. C'est ce qui rend la stratégie de test **lisible** pour un nouveau venu&nbsp;: chaque test est dans la catégorie qui correspond _à sa décision_.

## `IDENTIFIED_GAPS.md`

Tout gap (DATA, SPEC, SEC) a une entrée dans `IDENTIFIED_GAPS.md`. Le nom du test, la docstring, et l'entrée gaps doivent être **synchronisés**.

`CLAUDE.md`&nbsp;:

> **No SFD references outside `#` comments.** Test names, log messages, exception messages, docstrings&nbsp;—&nbsp;none contain `SFD §x.x`. Those references belong in `CURA_FRD.md` and in inline comments. The SFD number means nothing to someone reading a test report.

→ Les noms de tests sont **lisibles par un humain** (`Past date booking accepted`, pas `Test_FRD_9_7`). La référence `§9.7` vit dans le code _en tant que commentaire_ et dans `IDENTIFIED_GAPS.md`.
