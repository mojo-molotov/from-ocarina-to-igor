---
title: "10.03 — Workflows ocarina-example"
description: "Les workflows de ocarina-example : main_ci et dev_ci pour le lint et le typecheck, et e2e manuel avec service Redis et Firefox."
weight: 3
date: 2026-05-20
series: ["ci-cd"]
series_order: 3
---

# 10.03&nbsp;—&nbsp;Workflows `ocarina-example`

> Voir aussi [`../07-ocarina-example/11-ci.md`](../07-ocarina-example/11-ci.md)

## Vue d'ensemble

| Workflow      | Trigger                        | OS                                                                             | Effet                                                                         | Note              |
| ------------- | ------------------------------ | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ----------------- |
| `main_ci.yml` | push/PR main, dispatch         | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;3.14                            | `make check-coding-style` (mypy + ruff).                                      | Gate PR rapide    |
| `dev_ci.yml`  | push dev, dispatch             | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                | Idem                                                                          | Pour branches dev |
| `e2e.yml`     | `workflow_dispatch` (env `OC`) | ubuntu +&nbsp;service&nbsp;Redis +&nbsp;Firefox +&nbsp;geckodriver&nbsp;0.35.0 | Run complet de la suite + upload `.screenshots/` `.ocarina_logs/` `.reports/` | Manuel uniquement |

## vs `ocarina/main_ci.yml`

| Aspect                  | `ocarina/main_ci.yml`         | `ocarina-example/main_ci.yml` |
| ----------------------- | ----------------------------- | ----------------------------- |
| **Tests unitaires**     | Oui (pytest + cram)           | **Non**                       |
| **Allure history**      | Oui                           | Non                           |
| **GitHub Pages deploy** | Oui (Allure report)           | Non                           |
| **Matrice OS**          | Oui (ubuntu + windows)        | Oui (idem)                    |
| **Matrice Python**      | Optionnel (3.14 ou 3.14+3.15) | Non (3.14 seul)               |

→ `ocarina` _se teste_ (tests unitaires) en CI. `ocarina-example` n'est soumis qu'à des tests _statiques_ en CI&nbsp;;&nbsp;ses tests dynamiques (e2e) sont déclenchés _à la demande_ via `e2e.yml`.

## Le service Redis sidecar

```yaml
services:
  redis:
    image: redis:8.8.0
    ports: [6379:6379]
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

GitHub Actions "spins" un container Redis _en parallèle_ du job. Accessible sur `localhost:6379`. Healthcheck `redis-cli ping`.

Les tests peuvent donc utiliser Redis pour les locks distribués (`OTP_SEND_LOCK_KEY`) sans avoir à provisionner un Redis externe.

## `environment: OC`

```yaml
e2e:
  runs-on: ubuntu-latest
  environment: OC
```

- Contient les `secrets`&nbsp;: `IGOR_API_KEY`, `DASH_USERNAME`, `DASH_PASSWORD`.
- Peut requérir une approbation manuelle avant de lancer (utile si on consomme du quota).

L'utilisateur qui dispatch le workflow doit avoir accès à l'environment OC.

## Artefacts

```yaml
- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: e2e-traces
    path: |
      .screenshots/
      .ocarina_logs/
      .reports/
```

`if: always()`&nbsp;: upload même si le run fail. Pour pouvoir inspecter _pourquoi_ ça a fail.

1. `.screenshots/`&nbsp;: toutes les captures d'écran.
2. `.ocarina_logs/`&nbsp;: arbre de logs `cycle/campaign/suite/test.log`.
3. `.reports/`&nbsp;: sorties des plugins (DOCX + JSON).

## cache venv hashé sur pyproject

```yaml
- uses: actions/cache@v5
  with:
    path: .venv
    key: venv-${{ runner.os }}-py-${{ hashFiles('pyproject.toml') }}
```

`hashFiles('pyproject.toml')`&nbsp;: si `pyproject.toml` change (nouvelle dep, version bumpée), la cache key change&nbsp;→&nbsp;cache miss →&nbsp;réinstall propre.

## `Setup Firefox`

```yaml
- name: Setup Firefox
  uses: browser-actions/setup-firefox@<commit-sha>
```

Action publique qui installe Firefox version matching le `geckodriver` téléchargé.

Le _version pinning_ par SHA est utilisé partout pour toutes actions non-officielles (non préfixées par `actions/`) pour mitiger les risques de _Supply Chain Attack_.
