---
title: "Chapitre 08 — ocarina-with-ai-example"
description: "ocarina-with-ai-example, la suite e2e CURA Healthcare co-écrite par Claude Code : la preuve par l'exemple de la philosophie l'IA est le pont."
weight: 9
date: 2026-05-20
tags: ["ai-example"]
sidebar:
  open: true
---

# Chapitre 08&nbsp;—&nbsp;`ocarina-with-ai-example`

> Suite e2e CURA Healthcare **co-écrite par Claude Code**. C'est le _proof of concept_ vivant de la philosophie «&nbsp;_l'IA est le pont_&nbsp;».

## Plan

|  #  | Fichier                                                  | Sujet                                                                                                                        |
| :-: | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-ai-manifesto.md`](01-ai-manifesto.md)               | Le README et son constat «&nbsp;_Code&nbsp;: 99% Claude /&nbsp;Intelligence&nbsp;: 50-50_&nbsp;».                            |
| 02  | [`02-sut-cura.md`](02-sut-cura.md)                       | CURA Healthcare&nbsp;: SUT externe, PHP open source, Heroku eco-dyno.                                                        |
| 03  | [`03-canonical-documents.md`](03-canonical-documents.md) | Les 4 documents&nbsp;: `CLAUDE.md`, `CURA_FRD.md`, `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md`.                            |
| 04  | [`04-test-strategy.md`](04-test-strategy.md)             | Types de tests (happy /&nbsp;unhappy /&nbsp;edge /&nbsp;business attack /&nbsp;exploratory /&nbsp;regression).               |
| 05  | [`05-security-gaps.md`](05-security-gaps.md)             | Gaps sécurité&nbsp;: CSRF, session, rate-limit (G-SEC-1 à G-SEC-3).                                                          |
| 06  | [`06-data-gaps.md`](06-data-gaps.md)                     | Gaps data&nbsp;: visit_date sans validation, doublons (G-DATA-1 à G-DATA-2).                                                 |
| 07  | [`07-spec-gaps.md`](07-spec-gaps.md)                     | Gaps spec&nbsp;: ordre history, profile placeholder, redirects (G-SPEC-1 à G-SPEC-3).                                        |
| 08  | [`08-bfcache.md`](08-bfcache.md)                         | BFCache Chrome&nbsp;: B-BROWSER-1 (et A-ENV-1, A-ENV-2).                                                                     |
| 09  | [`09-ci-matrix.md`](09-ci-matrix.md)                     | CI&nbsp;: `ai_proof_ci.yml` + `ai_proof_e2e.yml` matrice Firefox/Chrome + warm-up Heroku + filtrage stacktrace ChromeDriver. |

## Success story

|              | Claude Code | Humain |
| ------------ | ----------- | ------ |
| Code écrit   | 99%         | 1%     |
| Intelligence | 50%         | 50%    |

> Almost every line was machine-written. The judgement behind it&nbsp;—&nbsp;what to test, what to distrust, when to dig and when to stop&nbsp;—&nbsp;was shared.

C'est l'incarnation de [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)&nbsp;:

> Avec l'IA, et des outils comme _Claude Code_, ce pari devient chaque jour plus solide. Le pont entre techniques et non-techniques n'est plus une couche d'abstraction.
>
> C'est l'IA elle-même. IA qui travaille sur de la donnée brute.

## Rappel du Holy Book

Trois choses _que ce projet n'est pas_, d'après le Holy Book (chapitre «&nbsp;_Utiliser Ocarina avec l'IA_&nbsp;»)&nbsp;:

> - Ne génère pas de tests de façon autonome.
> - Ne patche pas les hallucinations en CI&nbsp;; un échec déclenche `review-report` + `analyse-*`.
> - Ne réécrit pas la spec&nbsp;; seul `update-frd-and-tests` le fait, avec une ligne de révision.
> - Ne fait pas de tests de sécurité actifs. Jamais.

L'humain garde le contrôle. L'IA produit la mécanique.

## Singularité

1. **Lecture du PHP source pour trouver de vrais défauts**&nbsp;: CSRF absent, validation client-only, ordre d'history par soumission, etc.
2. **Tests d'attaques métier**&nbsp;: past-date booking, doublons, créneaux géographiquement impossibles.
3. **Divergence cross-browser traitée comme un finding**&nbsp;: BFCache Chrome qui restaure une `no-store` page après logout.

Chaque gap est documenté avec _file:line_ et _PHP evidence_, et matérialisé en _test intentionnellement rouge_ qui restera rouge tant que CURA n'est pas corrigé.

## Lectures connexes

- Le pari philosophique&nbsp;→&nbsp;[`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)
- Le rôle des _skills_ IA documentés sur le Holy Book&nbsp;→&nbsp;[`../09-holy-book/`](../09-holy-book/README.md)
- Le framework qu'il utilise&nbsp;→&nbsp;[`../02-ocarina/`](../02-ocarina/README.md)
