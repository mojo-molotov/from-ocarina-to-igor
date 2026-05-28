---
title: "00.04 — Relations entre les six dépôts"
description: "Les relations bilatérales entre les six dépôts : qui importe quoi, quels artefacts circulent, quels secrets et contrats sont partagés."
weight: 4
date: 2026-05-20
series: ["big-picture"]
series_order: 4
tags: ["otp"]
---

# 00.04&nbsp;—&nbsp;Relations entre les six dépôts

Chaque arête du graphe est un _contrat_&nbsp;: un secret, une URL, un type de payload, ou une version. On les détaille ici, par paire.

## `ocarina` ↔ `ocarina-example`

| Direction                               | Mécanisme                         |
| --------------------------------------- | --------------------------------- |
| `ocarina`&nbsp;→&nbsp;`ocarina-example` | `pip install ocarina` depuis PyPI |
| `ocarina-example`&nbsp;→&nbsp;`ocarina` | Aucune (l'exemple ne pousse rien) |

L'exemple **écrit ses propres adapters** au-dessus du framework&nbsp;:

- `lib/ext/ocarina/adapters/agnostic/act.py`&nbsp;→&nbsp;ajoute le hook `on_failure` qui transforme une page d'erreur HTTP (titre matché par `ERROR_PAGE_REGEX`) en `HttpErrorPageReachedError`.
- `lib/ext/ocarina/adapters/agnostic/match_page.py`&nbsp;→&nbsp;`create_match_page(raised_exceptions=transient_errors)`.
- `lib/ext/ocarina/adapters/agnostic/env_getters.py`&nbsp;→&nbsp;typed `EnvGetters[_CredsKeys, _ValuesKeys]`.
- `lib/ext/ocarina/adapters/selenium/test_suite.py`&nbsp;→&nbsp;fige `max_retries_per_test=8`, `transient_errors=...`, `autoscreen_on_fail=True`, propage `--only`/`--exclude`.
- `lib/ext/ocarina/adapters/selenium/test_campaign.py`&nbsp;→&nbsp;fige `max_workers=get_max_workers()`.

## `ocarina` ↔ `ocarina-with-ai-example`

- `pip install . ruff mypy mypy-extensions typing-extensions pre-commit` car l'exemple IA a la dépendance fixée dans son `pyproject.toml`&nbsp;: `ocarina>=1.0.3`.
- L'adapter `act` est **minimaliste** ici&nbsp;: pas de `on_failure` (CURA n'a pas de page d'erreur volontairement aléatoire à intercepter). Voir [`../08-ai-example/`](../08-ai-example/README.md)
- L'adapter `create_drivers_pool` est **surchargé** pour bâtir un Chrome _clean_ (password manager off, leak detection off). Voir [`../08-ai-example/06-data-gaps.md`](../08-ai-example/06-data-gaps.md)

## `ocarina-example` ↔ `igoristan`

| Direction                                 | Contrat                                    | Détail                                                            |
| ----------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------- |
| `ocarina-example`&nbsp;→&nbsp;`igoristan` | URLs publiques                             | Tout passe par `https://mojo-molotov.github.io/igoristan/<route>` |
| `igoristan`&nbsp;→&nbsp;`ocarina-example` | aucun (le SUT ne sait pas qu'il est testé) | &nbsp;—&nbsp;                                                     |

`src/constants/pages/`&nbsp;:

```
homepage.py                       → /igoristan/
dashboard.py                      → /igoristan/dashboard
random_loaders.py                 → /igoristan/random-loaders
sacred_upload.py                  → /igoristan/sacred-upload
corsicamon.py                     → /igoristan/corsicamon
chaotic_form.py                   → /igoristan/chaotic-form
madness.py                        → /igoristan/madness
random_error_page.py              → /igoristan/random-error
donkey_sausage_eater_detector.py  → /igoristan/donkey-sausage-eater-detector
```

## `igoristan` ↔ `tests-workers`

| Direction                               | Endpoint                                                                          | Auth                                                                                         |
| --------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `igoristan`&nbsp;→&nbsp;`tests-workers` | `GET https://tests-workers.vercel.app/api/otp?_user=<u>` (header `x-api-key`)     | OTP API key fournie par l'utilisateur dans l'UI                                              |
| `igoristan`&nbsp;→&nbsp;`tests-workers` | `GET https://tests-workers.vercel.app/api/corsicadex?id=<n>` (header `x-api-key`) | Corsicadex API key fournie par l'utilisateur dans l'UI                                       |
| `igoristan`&nbsp;→&nbsp;`tests-workers` | `GET https://tests-workers.vercel.app/api/corsicamon?<...>` (header `x-api-key`)  | Corsicamon API key (lecture seule, service tiers strict) fournie par l'utilisateur dans l'UI |
| `tests-workers`&nbsp;→&nbsp;`igoristan` | Aucun (`tests-workers` ne sait pas qu'il sert l'Igoristan)                        | &nbsp;—&nbsp;                                                                                |

- **SUT ↔ tests-workers**&nbsp;: l'Igoristan _consomme_ les endpoints **OTP** (push), **Corsicadex** et **Corsicamon** (lecture).
- **Tests e2e ↔ tests-workers**&nbsp;: `ocarina-example` _consomme uniquement_ l'endpoint **`/api/otp-history`** (lecture de l'historique). Il **n'utilise pas** directement Corsicadex, et il **ne pousse pas** sur OTP&nbsp;—&nbsp;il se contente de lire l'historique pour récupérer le code généré par le SUT.

## `ocarina-example` ↔ `tests-workers`

| Direction                                     | Endpoint                                                                                   | Auth                                      | Pourquoi                                                                          |
| --------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------- | --------------------------------------------------------------------------------- |
| `ocarina-example`&nbsp;→&nbsp;`tests-workers` | `GET https://tests-workers.vercel.app/api/otp-history` (header `x-api-key: $IGOR_API_KEY`) | `IGOR_API_KEY` ≡ `API_SECRET` côté Vercel | Récupérer l'historique des OTP pour piocher le bon (filtre `_user`, tri par date) |

Côté serveur (`tests-workers`), un unique `API_SECRET` est attendu sur le header `x-api-key` OU le query param `?apiKey=`. Voir [`../06-tests-workers/05-is-authorized.md`](../06-tests-workers/05-is-authorized.md)

## `ocarina-with-ai-example` ↔ CURA Healthcare

| Direction                     | URL                                        | Détail                                                                |
| ----------------------------- | ------------------------------------------ | --------------------------------------------------------------------- |
| `ai-example`&nbsp;→&nbsp;CURA | `https://katalon-demo-cura.herokuapp.com/` | Heroku eco-dyno, _s'endort_&nbsp;; un `warm-up` `curl` précède le run |
| CURA&nbsp;→&nbsp;`ai-example` | aucun                                      | &nbsp;—&nbsp;                                                         |

CURA n'est **pas un dépôt de l'écosystème**&nbsp;: c'est un SUT externe, open source PHP, hébergé par Katalon (`katalon-studio/katalon-demo-cura`). C'est un cas pratique pour le _proof_ IA. Les gaps observés (CSRF, etc.) n'étaient pas documentés à l'avance&nbsp;: ils ont été révélés **empiriquement** par le travail mené avec Claude. On peut lire le PHP pour _expliquer_ les gaps une fois découverts.

## `ocarina-holy-book` ↔ tous les autres

| Direction                  | Mécanisme                                                                             | Détail                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Holy Book&nbsp;→&nbsp;tout | Liens internes Markdown vers les autres dépôts (`mojo-molotov/ocarina`, etc.)         | Les chapitres «&nbsp;_Premiers pas_&nbsp;», «&nbsp;_Premiers obstacles du monde réel_&nbsp;», etc. citent en lien GitHub. |
| Tout&nbsp;→&nbsp;Holy Book | URL `Documentation` du `pyproject.toml` d'Ocarina pointe vers le Holy Book            | `Documentation = "https://mojo-molotov.github.io/ocarina-holy-book"`                                                      |
| LLMs&nbsp;→&nbsp;Holy Book | `llms.txt`, `llms-full.txt`, `CLAUDE.md`, `CLAUDE.slim.md` exposés en URLs canoniques | Voir [`../09-holy-book/06-public-resources.md`](../09-holy-book/06-public-resources.md)                                   |

## Secrets /&nbsp;variables d'environnement

| Variable                               | Producteur                                                        | Consommateur(s)                                                      | Rôle                                                                            |
| -------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `IGOR_API_KEY`                         | utilisateur (fichier `.env` localement, ou env GitHub `OC` en CI) | `ocarina-example` (`get_otp_history`, `retrieve_dashboard_otp_code`) | header `x-api-key` envoyé à `tests-workers`                                     |
| `API_SECRET`                           | utilisateur (`vercel env add API_SECRET`)                         | `tests-workers` (`isAuthorized.ts`)                                  | clé attendue (doit être ≡ `IGOR_API_KEY`)                                       |
| `UPSTASH_REDIS_REST_URL`               | utilisateur (`vercel env add`)                                    | `tests-workers` (`lib/redis.ts`)                                     | URL Upstash Redis                                                               |
| `UPSTASH_REDIS_REST_TOKEN`             | utilisateur (`vercel env add`)                                    | `tests-workers` (`lib/redis.ts`)                                     | token Upstash Redis                                                             |
| `DASH_USERNAME` /&nbsp;`DASH_PASSWORD` | utilisateur (`.env`)                                              | `ocarina-example` (`EnvGetters`)                                     | credentials du faux dashboard (par défaut `SacredFigatellu` /&nbsp;`figatellu`) |
| `REDIS_URL`                            | utilisateur (`.env`)                                              | `ocarina-example` (`lib/ext/redis/client.py`)                        | URL Redis local utilisé pour les **verrous distribués** (différent d'Upstash)   |
| `WAIT_TIMEOUT`                         | CI                                                                | `ocarina-with-ai-example` (`ai_proof_e2e.yml`)                       | `--wait-timeout 15`                                                             |
| `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`   | CI                                                                | `actions/*`                                                          | force Node 24 sur les actions JS                                                |
| `TZ`                                   | CI                                                                | `ocarina-holy-book/deploy.yml` (`Europe/Paris`)                      | rendu des dates dans la doc /&nbsp;PDF                                          |

## Diagramme des secrets

```
   ┌────────────────────────────────────────────────────────────────┐
   │                Utilisateur (humain ou CI env)                  │
   └────────┬──────────────────────────────┬────────────────────────┘
            │ IGOR_API_KEY                 │ UPSTASH_REDIS_REST_*
            │                              │ API_SECRET (= IGOR_API_KEY)
            ▼                              ▼
   ┌──────────────────────────┐   ┌──────────────────────────────────┐
   │ ocarina-example/.env     │   │ Vercel project envs              │
   │ (ou env "OC" en CI)      │   │ (tests-workers)                  │
   └────────────┬─────────────┘   └────────────────────┬─────────────┘
                │ x-api-key                            │
                ▼                                      │
   ┌──────────────────────────┐                        │
   │ GET /api/otp-history     │                        │
   └────────────┬─────────────┘                        │
                │                                      │
                │   (depuis l'UI de l'Igoristan)       │
                │   GET /api/otp?_user=u               │
                ▼                                      ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  tests-workers — isAuthorized.ts                                 │
   │  Compare le header x-api-key (ou ?apiKey=) contre API_SECRET     │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  Upstash Redis (UPSTASH_REDIS_REST_URL + TOKEN)                  │
   └──────────────────────────────────────────────────────────────────┘
```
