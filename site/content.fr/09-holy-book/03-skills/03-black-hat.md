---
title: "09.03.03 — Skills Black-hat"
description: "La famille de skills Black-hat exposés aux IA : des idéations de vulnérabilités de logique métier sans exécution, le test de sécurité y est fonctionnel et statique."
weight: 3
date: 2026-05-20
series: ["skills"]
series_order: 3
tags: ["holy-book"]
---

# 09.03.03&nbsp;—&nbsp;Skills Black-hat (6)

> **Idéations** de vulnérabilités de logique métier&nbsp;—&nbsp;pas d'exécution&nbsp;: «&nbsp;_security testing is functional and static, never active_&nbsp;».

## Listing (potentiellement non exhaustif)

| Skill                              | Cible                                                                                                                                    |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `business-logic-vulnerability-ideation`         | Faire tomber le produit via des chemins d'usage légitimes mais malicieux                                                                 |
| `incoherence-attack-ideation`      | Chaque étape prise isolément a l'air innocente&nbsp;; mais des combinaisons de ces étapes peuvent causer une incohérence dans le système |
| `persistence-attack-ideation`      | Tentatives répétées sur une action bloquée                                                                                               |
| `permission-appropriateness-audit` | Le modèle d'accès est-il lui-même approprié&nbsp;?                                                                                       |
| `bfcache-exposure-ideation`        | Attaques BFCache                                                                                                                         |
| `lateral-resource-ideation`        | IDOR via la barre d'adresse uniquement                                                                                                   |

## Périmètre

Tous ces skills _imaginent_ des attaques que **l'IA** pourrait formuler.

L'humain&nbsp;:

- Évalue la pertinence («&nbsp;_est-ce que ce gap est plausible&nbsp;?_&nbsp;»).
- Décide d'en faire un test (fonctionnel, via l'UI).
- Écrit le test (avec l'aide d'autres skills, p.ex. `extend-coverage`).

L'IA **ne lance jamais** d'attaque active. **C'est interdit.**

## `business-logic-vulnerability-ideation`

```
input  : les SFD + le code source du SUT (si open source)
output : liste d'usages légitimes mais malicieux
         exemples (CURA et apps similaires) :
            - past-date booking (G-DATA-1)
            - duplicate booking (G-DATA-2)
            - overlapping appointments (G-DATA-2)
            - book at non-business hours
            - book a date "100 ans dans le futur"
            - book with empty visit_date if HTML5 required bypassed
```

→ L'IA brainstorme. L'humain trie. Pour chaque idée retenue, on écrit un gap test (_assertive fail_ si le système devrait rejeter le comportement).

## `incoherence-attack-ideation`

```
exemple : geographically impossible same-day booking
          - book Hongkong CURA @ 10:00 (autorisé en soi)
          - book Tokyo CURA @ 12:00 (autorisé en soi)
          - combinaison : impossible (le patient ne peut pas téléporter)
```

## `persistence-attack-ideation`

```
exemple : un user bloqué par rate-limit / permission manquante
          → essaie 100 fois consécutives
          → vérifie si le système release après N attempts ou si le block tient
```

→ Sur CURA&nbsp;: pas de rate-limit (G-SEC-3), donc rien à tester. Sur d'autres SUTs, peut révéler des bugs de logique de blocage.

## `permission-appropriateness-audit`

```
input  : les SFD + l'observation du modèle d'accès
output : audit du modèle :
            - tel rôle a-t-il accès à telle ressource sans raison ?
            - tel endpoint requiert-il l'auth mais ne devrait pas ?
            - tel endpoint ne requiert pas l'auth mais devrait ?
```

→ Révèle souvent des gaps dans les SFD («&nbsp;_on n'avait pas pensé à ce cas_&nbsp;»).

## `bfcache-exposure-ideation`

```
input  : pages protégées par authentification du SUT
output : pour chaque page, recette back-then-reload :
            - login → naviguer vers la page → logout → back() → expect redirect
            - si pas de redirect : refresh() → expect redirect (= BFCache hit)
            - sinon : vrai gap server-side
```

## `lateral-resource-ideation`

```
input  : URLs de ressources avec ID (`/order/123`, `/user/456`, …)
output : pour chaque ressource, propose :
            - login en tant qu'utilisateur A
            - tenter d'accéder à `/order/<id_utilisateur_B>`
            - vérifier que le système refuse
```

C'est de l'**IDOR** (_Insecure Direct Object Reference_), mais via la **barre d'adresse uniquement**&nbsp;—&nbsp;pas de payload, pas de Proxy MITM. Juste un humain qui tape une URL.

## Discipline transversale

Tous les skills black-hat **imaginent**, mais n'exécutent **jamais**.

Si une idée méritte d'être testée&nbsp;:

1. L'humain valide l'idée.
2. La traduit en gap test fonctionnel (via `extend-coverage`).
3. Le test passe par l'UI/des comportements normaux couverts par le test fonctionnel.
4. Le test PASS ou FAIL (intentionnel).
5. Tout est documenté dans `IDENTIFIED_GAPS.md`.

Aucun payload, aucun cross-origin POST, aucun fuzzing scriptés. Cf. [`../../08-ai-example/05-security-gaps.md`](../../08-ai-example/05-security-gaps.md) section «&nbsp;«&nbsp;_Security testing is functional and static&nbsp;—&nbsp;never active_&nbsp;»&nbsp;».
