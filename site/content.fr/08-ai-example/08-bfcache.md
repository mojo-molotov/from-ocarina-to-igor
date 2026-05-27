---
title: "08.08 — BFCache Chrome (B-BROWSER-1) + artefacts d'environnement"
description: "Chrome restore une page no-store après logout, depuis le BFCache, alors qu'il s'agit d'une page protégée par authentification."
weight: 8
date: 2026-05-20
series: ["ai-example"]
series_order: 8
---

# 08.08&nbsp;—&nbsp;BFCache Chrome (B-BROWSER-1) + artefacts d'environnement

> Chrome restore une page `no-store` après logout, depuis le BFCache, alors qu'il s'agit d'une page protégée par authentification.

## B-BROWSER-1&nbsp;—&nbsp;Chrome nous emmerde avec son BFCache

### Symptôme

Après déconnexion, cliquer sur le bouton "précédent" afin d'être redirigé vers une page qui était protégée par authentification (par exemple&nbsp;: `history.php`)&nbsp;:

- **Chrome**&nbsp;: la page _reste affichée_ avec son contenu tel qu'il est affiché à un utilisateur encore authentifié. L'URL reste `history.php`, le serveur n'est pas recontacté pour valider ou invalider l'accès.
- **Firefox**&nbsp;: une nouvelle requête est envoyée au serveur, ce dernier voit que la session est morte, il redirige.

### Gap très ennuyeux

`history.php` envoie correctement&nbsp;:

- `Cache-Control: no-store, no-cache, must-revalidate`
- `Pragma: no-cache`
- `Expires`

Et l'invalidation server-side de la session est correcte.

**Mais le BFCache de Chrome restaure quand même la page** depuis un _snapshot_ local.

### Recette de confirmation&nbsp;: back-then-reload

```
back() → on est sur history.php, page authentifiée restaurée
   ↓ (rien n'a touché le serveur)
refresh() → reload force un round-trip serveur
   ↓
serveur : session morte → 302 vers homepage
   ↓
on est redirigé
```

- `back()` nous affiche à nouveau la page que l'on ne devrait plus voir **ET** `refresh()` provoque notre redirection&nbsp;→&nbsp;BFCache _hit_ confirmé.
- `back()` redirige immédiatement&nbsp;→&nbsp;invalidation _server-side_ qui fonctionne comme attendu.
- `back()` nous affiche à nouveau la page que l'on ne devrait plus voir **ET** `refresh()` ne nous redirige pas&nbsp;→&nbsp;l'invalidation _server-side_ est cassée (**anomalie**).

`CLAUDE.md`&nbsp;:

> **A confirmed BFCache exposure raises a dedicated, non-transient exception**&nbsp;—&nbsp;`BackForwardCacheExposureError` (`src/lib/errors.py`). Never a bare `AssertionError`; never a Selenium `WebDriverException`. The finding is deterministic and must never land in `transient_errors`.

### Exception dédiée

```python
# src/lib/errors.py
class BackForwardCacheExposureError(Exception):
    """The browser's back-forward cache exposed a logged-out authenticated view."""
```

Ce n'est PAS une exception de la collection `transient_errors`. Cette trouvaille est déterministe&nbsp;: on constate immédiatement le problème, ce n'est pas à considérer comme étant un _flake_.

### Tests associés

| Test                                 | Recipe                                                                                                                                 |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `post_logout_bfcache_exposure.py`    | back-then-reload&nbsp;: si back squatte une page qui ne devrait plus être affichée + refresh redirige&nbsp;→&nbsp;BFCacheExposureError |
| `post_logout_server_invalidation.py` | refresh direct&nbsp;:&nbsp;confirme que le serveur invalide bien (PASS)                                                                |
| `post_logout_frenetic_navigation.py` | back/forward stress (3 cycles)&nbsp;:&nbsp;tente de provoquer au max un timing mystérieux avec le BFCache                              |

- **`post_logout_bfcache_exposure`**&nbsp;: ÉCHEC sur Chrome, SUCCÈS sur Firefox.
- **`post_logout_server_invalidation`**&nbsp;: SUCCÈS sur les deux (le serveur fait sa part).

### Code

```python
class HistoryPage(SeleniumBackAndForwardNavigationMixin, SeleniumTitleMixin, POMBase):
    def verify_back_button_did_not_restore_view(self) -> Self:
        # On est sur history.php après back()
        pre_url = self._driver.current_url
        self._driver.refresh()
        try:
            WebDriverWait(self._driver, get_timeout()).until(
                ec.url_changes(pre_url)
            )
            # ✅ refresh a redirigé → server-side invalidation marche
            # → back() stayed put = BFCache hit
            raise BackForwardCacheExposureError(
                f"Browser BFCache restored authenticated view of {pre_url} after logout."
            )
        except TimeoutException:
            # refresh n'a pas redirigé → BFCache OR server-side fail
            # ... distinguer ...
            raise
```

→ La logique de distinction back→refresh est encapsulée dans le POM. Le scénario appelle juste `verify_back_button_did_not_restore_view`.

### «&nbsp;_Cross-browser difference is a finding_&nbsp;»

`CLAUDE.md`&nbsp;:

> **Never skip a test on the browser where it fails.**

Ce test reste actif sur les deux navigateurs.

1. Sur Chrome, il documente _déterministiquement_ la fragilité.
2. Sur Firefox, il documente que Firefox honore `no-store`.

### Recommandation à CURA

`IDENTIFIED_GAPS.md`&nbsp;:

> **Recommendation for CURA:** send `Clear-Site-Data: "cache", "cookies"` on the logout response so the snapshot is evicted regardless of the browser's back-forward-cache policy.

→ Header HTTP qui, normalement, force le navigateur à **détruire** le _snapshot_. Garantit le bon comportement même avec BFCache aggressif.

## A-ENV-1&nbsp;—&nbsp;Rapid POST drop sous `--workers 3`

### Symptôme

Sous `--workers 3`, un POST _rapide et consécutif_ d'un des trois workers parallèles fail intermittemment.  
Observé sur&nbsp;:

- `Appointments - Saturation` (5 bookings successifs).
- `Journey - History ordered ...` (2 bookings successifs).

### Cause

_"Heroku eco-dyno concurrency limit hit"._ C'est lié à l'infra sur laquelle est déployée le SUT. En vérifiant en _single-worker_, 2 réservations consécutives passent en 200-600ms.

### Gestion de la flakiness

`TimeoutException ⊆ WebDriverException`&nbsp;→&nbsp;ça part dans `transient_errors`&nbsp;→&nbsp;auto-retry.  
Un fail survivant aux retries indique que l'on a potentiellement atteint un niveau de contention trop important, ce ne serait pas forcément une régression et mériterait une _analyse complémentaire_ côté _DevOps_.

## A-ENV-2&nbsp;—&nbsp;Modale de détection d'un mot de passe faible (Chrome)

### Symptôme

Sur Chrome uniquement, après un login réussi&nbsp;: toute action subséquente (clic, frappe clavier, touche entrée) ne faisait **rien**. Après analyse, on s'est rendu compte que c'était dû à une modale native dans Chrome&nbsp;: «&nbsp;_your password has leaked_&nbsp;» apparaissait et plantait les pas de test.

### Cause

`ThisIsNotAPassword` est dans la _publicly-leaked credentials database_ de Google. Le _gestionnaire de mots de passe_ de Chrome le détecte et hurle juste après la moindre connexion à l'application. _C'est typiquement un problème d'environnement de test, et qui plus est qui concerne le testeur directement._

### Résolution

`src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py`&nbsp;:

```python
options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
})
options.add_argument("--disable-features=PasswordLeakDetection")
```

→ Désactive le _gestionnaire de mots de passe_ de Chrome + la fonctionnalité de "leak detection".  
La modale non pertinente n'apparaît plus.

### `IDENTIFIED_GAPS.md`

> **Why it stays documented:** the entry preserves _why_ the chrome driver adapter exists&nbsp;—&nbsp;delete the adapter and this artifact returns.

→ Mémoire. Si un _refactor_ futur supprime l'adapter custom, on _saura_ pourquoi il avait été ajouté.

## Conventions sémantiques

| Préfixe | Catégorie                            | Exemple                                               |
| ------- | ------------------------------------ | ----------------------------------------------------- |
| `G-`    | Gap (CURA est défaillant)            | `G-SEC-1`, `G-DATA-1`, `G-SPEC-1`                     |
| `B-`    | Browser (comportement du navigateur) | `B-BROWSER-1`                                         |
| `A-`    | Artefact d'environnement             | `A-ENV-1` (dyno contention), `A-ENV-2` (Chrome modal) |
