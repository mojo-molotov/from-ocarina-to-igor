---
title: "08.05 — Gaps sécurité (G-SEC-1 à G-SEC-3)"
description: "Les trois gaps de sécurité de CURA documentés par ocarina-with-ai-example, observés par tests fonctionnels et jamais exploités activement."
weight: 5
date: 2026-05-20
series: ["ai-example"]
series_order: 5
---

# 08.05&nbsp;—&nbsp;Gaps sécurité (G-SEC-1 à G-SEC-3)

> Trois gaps de sécurité documentés. Pas exploités activement (cf. règle «&nbsp;_security testing is functional and static, never active_&nbsp;»), mais observés via tests fonctionnels.

## G-SEC-1&nbsp;—&nbsp;Pas de jeton CSRF sur les formulaires côté front-end

### Symptôme

Le `<form>` rendu côté Heroku **ne contient pas** de CSRF token.

### Source

`views/page_appointment.php` du repo GitHub _appelle_ `$antiCSRF->insertHiddenToken()` avant le bouton submit. Mais sur la **version déployée**, ce token n'apparaît **pas** dans le HTML.

→ Divergence intention du code source vs livrable.

### Authentification

`authenticate.php` ne valide _pas_ le CSRF non plus&nbsp;:

```php
_f::login(_f::post("username"), _f::post("password"));
```

Pas de check `$antiCSRF->isValidRequest()`.

### Bug bonus

Même si le formulaire _avait_ le token&nbsp;: `$antiCSRF` n'est **jamais défini** dans le code.  
C'est une expression évaluée avec une variable indéfinie.

### Impact

Les POSTs cross-origin vers `appointment.php` ou `authenticate.php` (avec les bons noms de champs) réussissent inconditionnellement. Il est possible d'usurper un utilisateur de CURA en exploitant cette vulnérabilité.

### Approche de test

**Aucun test automatisé** sur ce gap dans la suite actuelle. La trouvaille est strictement documentée dans `IDENTIFIED_GAPS.md` (entrée G-SEC-1) avec preuve par lecture statique du PHP source et inspection manuelle du DOM rendu sur le déploiement Heroku.

Ce gap _pourrait_ être matérialisé par un test fonctionnel mais ne l'est pas en l'état.

## G-SEC-2&nbsp;—&nbsp;`_f::logout()` ne détruit pas le cookie

### Symptôme

Après `GET authenticate.php?logout`, le browser garde le cookie `PHPSESSID` avec la même valeur. La session est effacée côté serveur, mais le cookie reste.

### Source

```php
public function logout() {
    session_unset();
    $this->antiCSRF->unsetToken();
    return session_destroy();
}
```

`session_destroy()` détruit les données serveur. **Mais** ne fait pas `setcookie(session_name(), '', time() - 42000, '/')` qui forcerait le navigateur à supprimer le cookie.

### Pourquoi c'est important

Risque d'attaque combinée avec G-SEC-1.

### Recommandation

Appeler `setcookie(session_name(), '', time() - 42000, '/')` _avant_ `session_destroy()`.

### Approche de test

| Test                              | Vérifie                                                                                            |
| --------------------------------- | -------------------------------------------------------------------------------------------------- |
| `post_logout_access`              | Après logout, la navigation vers `/history.php` redirige (URL change → session check côté serveur) |
| `post_logout_server_invalidation` | Un reload forcé après logout (qui contourne le BFCache) redirige aussi                             |
| `post_logout_bfcache_exposure`    | Le bouton "back" après logout ne restaure pas la vue authentifiée depuis le BFCache                |
| `post_logout_frenetic_navigation` | Back/forward stress après logout, la page protégée reste verrouillée N cycles                      |
| `rapid_logout_relogin`            | Cycles rapides logout/login, intégrité de session (probe)                                          |

Tous ces tests **PASSENT quand CURA se comporte correctement** (la session _est_ invalidée côté serveur). G-SEC-2 (la persistance du cookie côté navigateur) reste documenté dans `IDENTIFIED_GAPS.md` mais sans test fonctionnel dédié, parce qu'isolément le cookie ne donne pas accès aux pages protégées, `session_destroy()` côté serveur fait le travail, et ces 5 tests prouvent que cette partie du travail est fait.

## G-SEC-3&nbsp;—&nbsp;Pas de rate-limit, pas de lockout, pas de CAPTCHA

### Source

```php
if ($user === USERNAME && $password === PASSWORD) {
    ...
}
```

`_f::login()` fait une comparaison `===` (case-sensitive et pas de _type juggling_). **Mais aucun throttle, aucun lockout, aucun CAPTCHA**.

### Risque

Risque de bruteforce.

### Hors-périmètre

> Out of scope to exploit on a demo app; documented because the implementation has no defensive depth.

→ Documentation _passive_. Pas de test qui bruteforce (interdit par la règle «&nbsp;_security testing is functional and static, never active_&nbsp;»).

C'est un cas où `IDENTIFIED_GAPS.md` fait office de _documentation de trouvailles_ sans test automatisé correspondant. La règle «&nbsp;_gap test required if user-facing_&nbsp;» ne s'enclenche pas, parce que ce n'est pas un comportement utilisateur normal que de bruteforcer un formulaire d'authentification.

## Discipline _static-only_ pour ne pas déborder du périmètre fonctionnel

`CLAUDE.md`&nbsp;:

> This is a **functional** test suite. Its scope ends at _what a real user can do through the browser_, plus _reading source for gap analysis_. Inside that scope:
>
> - Static analysis is welcome and encouraged.
> - Functional tests that exercise security-relevant behaviour through the **normal UI/HTTP path**&nbsp;—&nbsp;submitting an empty visit date through the real form, attempting a duplicate booking through the real form, asserting no CSRF input by reading the rendered HTML, checking that the back-button doesn't expose a logged-out view by pressing back&nbsp;—&nbsp;are fine.
>
> **Forbidden, no exceptions:**
>
> - Crafted attack payloads (SQL injection, XSS, command injection, header pollution, path traversal, deserialisation, …).
> - Token tampering, signature stripping, cookie forgery, session-fixation attempts, forced-browsing fuzzers.
> - Cross-origin POSTs constructed outside the suite, scripted directory enumeration, DOS, rate-floods.

| Action                                                | Catégorie           | Status      |
| ----------------------------------------------------- | ------------------- | ----------- |
| Soumettre un formulaire sans date via la vraie UI     | Fonctionnel         | ✅ OK       |
| Vérifier l'absence de CSRF token en lisant le DOM     | Fonctionnel         | ✅ OK       |
| Tenter de multiplier les réservations via la vraie UI | Fonctionnel         | ✅ OK       |
| Presser le bouton "précédent" après s'être déconnecté | Fonctionnel         | ✅ OK       |
| Envoyer `'  OR 1=1 --` dans le champ username         | **Crafted payload** | ❌ INTERDIT |
| Tampering du cookie `PHPSESSID`                       | **Tampering**       | ❌ INTERDIT |
| Cross-origin POST forgé                               | **Hors UI normale** | ❌ INTERDIT |
| Brute-force du login                                  | **Rate flood**      | ❌ INTERDIT |

→ Si on veut tester ces choses _activement_, c'est un autre projet (Burp /&nbsp;ZAP /&nbsp;sqlmap /&nbsp;contrat de prestation dédié).

## Schéma (brèches sécurité)

```
                          ┌────────────────────────────────────────┐
                          │           CURA / PHP                   │
                          ├────────────────────────────────────────┤
                          │                                        │
        G-SEC-1 :         │  page_login.php / page_appointment.php │
        forms sans CSRF   │  → pas de <input name="csrf_token">    │
        ↑                 │                                        │
        │                 │  authenticate.php :                    │
        │                 │   _f::login(...)  sans isValidRequest  │
        │                 │                                        │
        │                 │  appointment.php :                     │
        │                 │   $antiCSRF->isValidRequest()          │
        │                 │   ← $antiCSRF n'est pas défini ici     │
        │                 │                                        │
        └─────────────────┤                                        │
        G-SEC-2 :         │  functions.php / _f::logout() :        │
        cookie reste      │   session_destroy()                    │
        ↑                 │   ← pas de setcookie(... time()-42000) │
        │                 │                                        │
        └─────────────────┤                                        │
        G-SEC-3 :         │  _f::login() :                         │
        no rate-limit     │   if ($user === USERNAME && ...)       │
        ↑                 │   ← pas de throttle, lockout, captcha  │
        │                 │                                        │
        └─────────────────┤                                        │
                          └────────────────────────────────────────┘
```
