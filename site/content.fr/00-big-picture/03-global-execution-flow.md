---
title: "00.03 — Flux d'exécution global d'une campagne e2e"
description: "Le flux d'exécution complet d'une campagne e2e Ocarina, du parsing CLI jusqu'au SUT, en passant par la pool de drivers, le cycle et les plugins."
weight: 3
date: 2026-05-20
series: ["big-picture"]
series_order: 3
tags: ["selenium"]
---

# 00.03&nbsp;—&nbsp;Flux d'exécution global d'une campagne e2e

Un `python -u src/main.py …` lancé sur l'une des deux suites
(`ocarina-example` ou `ocarina-with-ai-example`) déclenche cette chaîne&nbsp;:

```
USER  ────────────────────────────────────────────────────────────────────
       python -u src/main.py --browser firefox --workers 3 [...]
              │
              ▼
       (1) parse CLI
           CliStoreSingleton.push(create_selenium_auto_cli_store())
              │
              ▼
       (2) build pool
           create_selenium_drivers_pool(max_size=N)
              │
              ▼
       (3) warm-up dépendances externes
           - Redis (ocarina-example)
           - Heroku dyno (ai-example, via curl --retry 6)
              │
              ▼
       (4) bootstrap(
              test_cycle  = create_e2e_test_cycle(drivers_pool),
              run_plugins = lambda results: run_plugins(
                                generate_docx_proof, generate_json_results,
                                exceptions_logger=...),
              post_exec   = pretty_print_results + sys.exit(1) si fail
           )
              │
OCARINA  ─────┼──────────────────────────────────────────────────────────
              │
              ▼
       (5) TestCycle.run_all (saturate_workers=True)
              ├─ smoke_tests_campaigns      [mode : fail-fast | wait-for-all]
              │     └─ TestCampaign.run_all
              │           └─ TestSuite.run (max_workers, saturate_workers)
              │                 └─ ThreadPoolExecutor → TestFlow.run
              │                       └─ pool.acquire() → TestExecutor.execute
              │                             ├─ setup()                  (optionnel)
              │                             ├─ watchers.start()         (daemon threads)
              │                             ├─ chain_runners            (DSL Railway)
              │                             ├─ watchers.stop()
              │                             └─ teardown()               (toujours)
              ├─ campaigns (main)
              │  (skippées si un smoke a fail)
              │
SUT   ────────┼────────────────────────────────────────────────────────────
              │
              ▼
       Selenium WebDriver ⇄ navigateur réel
       parfois : OTP HTTP GET + Redis (côté ocarina-example)
              │
              ▼
       (6) run_plugins(results)
              ├─ generate_docx_proof  (lit l'arbre de logs, fabrique des .docx)
              ├─ generate_json_results (sérialise results en .json)
              ├─ d'autres si déclarés (parallélisés via ThreadPoolExecutor)
              │
              ▼
       (6') post_exec(results)
              ├─ pretty_print_results (ANSI, hiérarchique)
              └─ has_test_cycle_failed → sys.exit(1) le cas échéant
```

## Détail des étapes

### (1) Parse CLI

`create_selenium_auto_cli_store()` détecte l'OS via `platform.system()`&nbsp;:

| OS             | Browsers proposés             |
| -------------- | ----------------------------- |
| Windows        | `chrome`, `firefox`, `edge`   |
| macOS (Darwin) | `chrome`, `firefox`, `safari` |
| Linux          | `chrome`, `firefox`           |

Toutes les validations (`--driver-path` doit pointer un fichier, `--workers ≥ 1`, mutex `--only` /&nbsp;`--exclude`, etc.) sont écrites _avec `validate(...)`_&nbsp;: la chaîne d'invariants d'Ocarina est utilisée pour valider Ocarina lui-même. Détail&nbsp;: [`../02-ocarina/11-opinionated/03-selenium-cli.md`](../02-ocarina/11-opinionated/03-selenium-cli.md)

### (2) Build pool

`create_selenium_drivers_pool(max_size=N)` crée un `WebDriversPool` adossé à un `Semaphore(N)` et une `Queue(N)`. Voir [`../02-ocarina/10-infra/01-drivers-pool.md`](../02-ocarina/10-infra/01-drivers-pool.md)

> Détail&nbsp;: la version **`ai-example`** _surcharge_ cette construction pour construire différemment Chrome (password manager désactivé, leak detection désactivée). Voir [`../08-ai-example/06-data-gaps.md`](../08-ai-example/06-data-gaps.md)

### (3) Warm-up

| Dépendance  | Cmd                                                          | Why                                                                                                  |
| ----------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Redis       | `warmup_redis_client()` (`StrictRedis.from_url(...).ping()`) | Couper la latence de cold-start, vérifier que Redis répond                                           |
| Heroku dyno | `curl -sf --retry 6 --retry-delay 5 …`                       | CURA tourne sur un eco-dyno Heroku qui s'endort&nbsp;; Napoléon désapprouve les tests sur dyno froid |

### (4) Bootstrap

`bootstrap(test_cycle, run_plugins, post_exec, saturate_workers=True)`&nbsp;:

1. `results = test_cycle.run_all(saturate_workers=saturate_workers)`
2. `run_plugins(results)`
3. `if post_exec: post_exec(results)`

L'ordre est strict&nbsp;: **cycle&nbsp;→&nbsp;plugins →&nbsp;post_exec**. `post_exec` est l'endroit pour brancher `pretty_print_results` + `sys.exit(1)`.

### (5) TestCycle

Voir [`../02-ocarina/05-orchestration/`](../02-ocarina/05-orchestration/README.md)&nbsp;: chaque niveau (`Test`, `TestExecutor`, `TestFlow`, `TestSuite`, `TestCampaign`, `TestCycle`) a son propre fichier.

| Niveau         | Rôle                                                                                                   | Concurrence    |
| -------------- | ------------------------------------------------------------------------------------------------------ | -------------- |
| `Test`         | Cas de test (`spawn` injecte driver+logger)                                                            | &nbsp;—&nbsp;  |
| `TestExecutor` | Une **tentative** (setup&nbsp;→&nbsp;watchers.start →&nbsp;chain →&nbsp;watchers.stop →&nbsp;teardown) | &nbsp;—&nbsp;  |
| `TestFlow`     | Boucle de **rejeu** (1+max_retries, backoff linéaire)                                                  | &nbsp;—&nbsp;  |
| `TestSuite`    | Suite parallèle (ThreadPoolExecutor) + saturation + filtrage IDs                                       | **N threads**  |
| `TestCampaign` | Séquence de suites (séquentielle entre suites, parallèle dedans)                                       | suite-level    |
| `TestCycle`    | Smoke + main, le `mode` (fail-fast \| wait-for-all) ne concerne **que les smokes**                     | campaign-level |

### (6) Plugins post-exec

`run_plugins(*plugins, exceptions_logger)`&nbsp;:

- **1 plugin**&nbsp;→&nbsp;exécution séquentielle&nbsp;;
- **N plugins**&nbsp;→&nbsp;exécution **parallèle** via `ThreadPoolExecutor(max_workers=len(plugins))`.
- Si un plugin lève, l'exception est **loggée** et les autres continuent.
- **Les plugins sont, par construction, indépendants les uns des autres**&nbsp;: pas de _hooks_ inter-plugins, pas de coordination.

Les deux plugins câblés dans les démos&nbsp;:

- `generate_docx_proof(logs_root, output_root, logger)`&nbsp;: un `.docx` par cas de test, screenshots inclus, dates UTC converties en heure locale.
- `generate_json_results(results, output_dir, logger)`&nbsp;: un `.json` contenant un rapport de test minimaliste.

**Taxonomie automatisée**&nbsp;: Ocarina dérive la taxonomie d'arborescence directement de ce que déclare le code (Campaign /&nbsp;Suite /&nbsp;Test). Les logs et les rapports DOCX sont _automatiquement_ déposés dans des dossiers qui reproduisent cette taxonomie déclarée&nbsp;: pas de configuration séparée à maintenir.

Voir [`../02-ocarina/11-opinionated/05-plugins-reports.md`](../02-ocarina/11-opinionated/05-plugins-reports.md)

## Diagramme de séquence (cas authentification OTP)

Cas d'école&nbsp;: le test «&nbsp;_Login with OTP_&nbsp;» d'`ocarina-example`. Trois acteurs&nbsp;: la suite Ocarina, le SUT Igoristan, et `tests-workers`.

```
Suite Ocarina                      Igoristan (UI)              tests-workers / Upstash Redis
────────────────                   ──────────────              ──────────────────────────────
TestCycle.run_all
    │
    ├─ TestSuite.run (max_workers=N)
    │      │
    │      ├─ ThreadPoolExecutor ⇒ N TestFlow.run en parallèle
    │      │       │
    │      │       └─ TestFlow.run(test)
    │      │             │
    │      │             ├─ pool.acquire() → driver frais
    │      │             │
    │      │             ├─ TestExecutor.execute(driver)
    │      │             │     │
    │      │             │     ├─ setup()  (none ici)
    │      │             │     ├─ watchers.start() (none ici)
    │      │             │     ├─ chain_runners[0..n].run() :
    │      │             │     │     drive_page : OPEN login page
    │      │             │     │     drive_page : type creds, tick OTP, click "Send"
    │      │             │     │                       │
    │      │             │     │                       └──► fetch /api/otp?_user=u
    │      │             │     │                              │             │
    │      │             │     │                              │             ├─► GET /api/otp?_user=u
    │      │             │     │                              │             │     redis.set otp:<ts>:<uuid> = {event}
    │      │             │     │                              │ ◄─── 200 {otpCode}
    │      │             │     │                       UI affiche écran OTP
    │      │             │     │
    │      │             │     │     drive_page : retrieve_dashboard_otp_code()
    │      │             │     │                       │
    │      │             │     │                       └──── HTTP GET /api/otp-history ───┐
    │      │             │     │                                                          │
    │      │             │     │                                                          ▼
    │      │             │     │                                                  SCAN otp:* (batch 100)
    │      │             │     │                      ┌─────────── 200 [events] ──────────┘
    │      │             │     │                      │
    │      │             │     │                      ▼
    │      │             │     │     filter by _user, sort ASC, pick the first match
    │      │             │     │
    │      │             │     │     drive_page : type OTP, confirm
    │      │             │     │                  → AUTHENTICATED_WITH_MFA
    │      │             │     ├─ watchers.stop() (none)
    │      │             │     └─ teardown() (none)
    │      │             │
    │      │             ├─ pool.release() → driver disposed
    │      │             │
    │      │             └─ return (TestResult, steps_count, test_id)
    │      │
    │      └─ wait(futures, FIRST_COMPLETED) — aggregates
    │
    └─ ... next campaigns

```

## `TestFlow.run`&nbsp;—&nbsp;Anatomie d'un échec transitoire

```
attempt = 1
                    ┌─ pool.acquire ─ driver frais ──┐
attempt 1  ────────►│ TestExecutor.execute(...)      │  → outcome
                    └────────────────────────────────┘
   │
   ├─ outcome.skipped         → return (None, -1, id)
   ├─ outcome.setup_failed    → setup_failures += 1
   ├─ outcome.should_retry &&
   │  attempt < max_attempts  → logger.cleanup(); time.sleep(attempt); continue
   └─ break

   …

attempt N ────────► (idem)

   …

if setup_failures >= max_attempts:
    return (None, -1, id)        # ⚠️  test SKIPPED, pas FAILED
return (last_result, last_steps_count, id)
```

| Paramètre              | Défaut                                                                                                                                                    | Source               |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `max_retries_per_test` | **8** (i.e. 9 tentatives au total&nbsp;—&nbsp;«&nbsp;_9 vies comme un chat_&nbsp;» 🐱)                                                                    | `TestSuite.__init__` |
| `transient_errors`     | `()` au niveau du framework&nbsp;; défini par l'utilisateur pour son projet (`WebDriverException`, `ReadTimeoutError`, `HttpErrorPageReachedError`, etc.) | adapter projet       |
| Backoff                | `time.sleep(attempt)`&nbsp;—&nbsp;linéaire 1s, 2s, 3s, …                                                                                                  | `TestFlow.run`       |

Voir [`../02-ocarina/05-orchestration/03-test-flow-retries.md`](../02-ocarina/05-orchestration/03-test-flow-retries.md) pour le détail.
