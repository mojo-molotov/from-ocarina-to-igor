---
title: "08.02 — CURA Healthcare (SUT)"
description: "CURA Healthcare, le SUT externe de ocarina-with-ai-example : application PHP open source hébergée sur un dyno Heroku, credentials publics."
weight: 2
date: 2026-05-20
series: ["ai-example"]
series_order: 2
---

# 08.02&nbsp;—&nbsp;CURA Healthcare (SUT)

## La première victime d'Ocarina

- **Hébergement**&nbsp;: https://katalon-demo-cura.herokuapp.com/
- **Source**&nbsp;: https://github.com/katalon-studio/katalon-demo-cura (PHP, open source, MIT)
- **Hébergeur**&nbsp;: Heroku eco-dyno (qui s'endort après inactivité)
- **Credentials**&nbsp;: `John Doe` /&nbsp;`ThisIsNotAPassword` (publics, hardcodés sur la page login)

## Périmètre

| Page                   | Fonction                                                                        |
| ---------------------- | ------------------------------------------------------------------------------- |
| `/`                    | Marketing homepage                                                              |
| `/profile.php#login`   | Login                                                                           |
| `/appointment.php`     | Form de booking (facility, programs, hospital_readmission, visit_date, comment) |
| `/confirmation.php`    | Confirmation du booking                                                         |
| `/history.php`         | Historique des bookings du user                                                 |
| `/profile.php#profile` | Page Profil (placeholder vide&nbsp;—&nbsp;gap §G-SPEC-2)                        |

## Pourquoi cibler CURA

1. **Open source**. On peut lire le PHP pour comprendre _pourquoi_ tel comportement.
2. **Beaucoup de gaps**. Riche terrain de _findings_.
3. **Public, démo**. Pas d'autorisation à demander. Stable (maintenu par Katalon).

Plus une raison tacite&nbsp;: Katalon est un éditeur de framework de test concurrent (_Katalon Studio_).  
C'est joliment _poétique_ de tester _leur_ app démo avec _Ocarina_.

## `CURA_FRD.md`

> **À propos de `CURA_FRD.md`.** CURA est une app démo publique&nbsp;—&nbsp;**aucune documentation fonctionnelle n'existe nulle part.** `CURA_FRD.md` a été écrit de zéro, entièrement par IA, en explorant l'app live et en lisant son PHP open source. C'est une spec _reconstruite_&nbsp;—&nbsp;du _reverse engineering_ par IA de ce que CURA fait et de ce qu'un système de santé comme lui _devrait_ faire&nbsp;—&nbsp;ce document n'est néanmoins pas une source d'autorité.

1. Sessions d'exploration manuelle de l'app live.
2. Lecture du PHP via `gh api repos/katalon-studio/katalon-demo-cura/contents/...`.
3. Hypothèses sur _ce qu'un système de santé devrait faire_ (§9).

La SFD est l'**arborescence sémantique** sur laquelle les tests sont basés.  
Chaque test cite un `REQ-X-N` ou un `§9.x` (gap).

## Périmètre des SFD

| Section | Contenu                                                               |
| ------- | --------------------------------------------------------------------- |
| 1-3     | Executive summary, system overview, roles                             |
| 4       | Functional requirements (Auth, Appointment, History, Profile)         |
| 5       | Element IDs (un par champ de formulaire)                              |
| 6       | URL map (`/profile.php#login`, etc.)                                  |
| 7       | Business rules                                                        |
| 8       | Error handling                                                        |
| **9**   | **Known bugs /&nbsp;gaps** (CSRF, validation, session, BFCache, etc.) |

**Chaque gap a un ID stable (`§9.1`, `§9.2`, ...) référencé par les tests.**

## `IDENTIFIED_GAPS.md`

| Document             | Contenu                                                                             | Cible        |
| -------------------- | ----------------------------------------------------------------------------------- | ------------ |
| `CURA_FRD.md` §9     | Description du gap (impact, recommandation, test ref)                               | Stakeholders |
| `IDENTIFIED_GAPS.md` | Inventaire **technique**&nbsp;: citations PHP _file:line_, recettes de reproduction | Mainteneurs  |

```markdown
### G-SEC-1 — No CSRF token on deployed forms

- **Where:** `views/page_login.php` (login form), `views/page_appointment.php` (appointment form) on https://katalon-demo-cura.herokuapp.com/.
- **Github source vs deployment:** `page_appointment.php` in the github repo calls `$antiCSRF->insertHiddenToken()` before the submit button. The
  **deployed** Heroku app does not render a hidden token input — verified by reading the live `<form>` HTML; the only fields are
  `facility / hospital_readmission / programs / visit_date / comment`. Reproduce by driving a Selenium browser through login → appointment and reading
  `document.querySelector('form').outerHTML`.
- **Authentication side:** `authenticate.php` performs no CSRF validation on login either — it directly calls
  `_f::login(_f::post("username"), _f::post("password"))` without consulting `$antiCSRF`.
- **Bonus bug:** Even if the form _did_ include a token, `appointment.php` checks `$antiCSRF->isValidRequest()` where `$antiCSRF` is never defined in
  that file (`security.php`'s class isn't instantiated there). The expression evaluates against an undefined variable; the check is no-op.
- **Impact:** Cross-origin POSTs to `appointment.php` and `authenticate.php` with the right field names succeed unconditionally for the demo account.
- **SFD ref:** §9.9.
```

→ Précision _file:line_, recipe de reproduction, SFD cross-ref.  
C'est de la **documentation forensique**.

## Heroku dyno

CURA tourne sur un Heroku **eco-dyno**&nbsp;:

1. Sleep après ~30 min sans trafic.
2. Cold start.

D'où l'étape «&nbsp;_warm-up_ Heroku dyno&nbsp;» dans `ai_proof_e2e.yml`&nbsp;:

```bash
curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
  --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
echo "Dyno is warm"
```

```
# CURA runs on a Heroku dyno that sleeps after inactivity.
# Tests hitting a cold dyno produce timeouts (false fails) and slow
# confirmations (false passes on gap tests). Wake it explicitly
# before any browser opens.
```

## `A-ENV-1`&nbsp;: contention dyno sous `--workers 3`

> ### A-ENV-1&nbsp;—&nbsp;Rapid-POST drop under `--workers 3` against the shared dyno
>
> - **Symptom:** Under `--workers 3`, a **rapid second-in-a-row POST** from one of the three parallel workers intermittently fails to redirect within 10 s.
> - **Matrix-wide, not browser-specific:** the trigger is three browser instances hammering one Heroku eco dyno, not any one browser.
> - **Not a CSRF issue:** per G-SEC-1, the deployed forms have no token.
> - **Not a SUT bug at single-worker:** solo (one worker) books two consecutive appointments cleanly in ~200–600 ms each.
> - **Cause:** Heroku eco-dyno concurrency limit hit by near-simultaneous POSTs from parallel workers.
> - **Handling:** `TimeoutException ⊆ WebDriverException` is in `transient_errors`, so a single occurrence auto-retries. A failure that survives all
>   retries is this artifact at full contention, not a regression.

## `A-ENV-2`&nbsp;: Chrome password breach detection

> ### A-ENV-2&nbsp;—&nbsp;Chrome password-breach modal swallows all input after login (resolved)
>
> - **Symptom (historical):** On chrome only, a test that logged in and then did _anything_&nbsp;—&nbsp;click, `send_keys`, even `Keys.ENTER` on a focused submit
>   button&nbsp;—&nbsp;saw the input silently do nothing.
> - **Cause:** the demo password `ThisIsNotAPassword` is a publicly-leaked credential, so Chrome's password manager raised a native breach-detection
>   modal on every successful login. The modal is browser chrome&nbsp;—&nbsp;invisible to `elementFromPoint`, doesn't block JS&nbsp;—&nbsp;but it captures every real input
>   event.
> - **Resolution:** `src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py` builds chrome with the consumer password manager off.
> - **Why it stays documented:** the entry preserves _why_ the chrome driver adapter exists&nbsp;—&nbsp;delete the adapter and this artifact returns.

## Lectures connexes

- Les gaps détaillés&nbsp;: [`05-security-gaps.md`](05-security-gaps.md), [`06-data-gaps.md`](06-data-gaps.md), [`07-spec-gaps.md`](07-spec-gaps.md), [`08-bfcache.md`](08-bfcache.md)
- Le `create_drivers_pool` custom (Chrome clean)&nbsp;: [`09-ci-matrix.md`](09-ci-matrix.md)
