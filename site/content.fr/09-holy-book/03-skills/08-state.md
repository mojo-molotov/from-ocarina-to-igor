---
title: "09.03.08 — Skill State"
description: "Le skill State exposé aux IA, question-state : interroger l'état de l'environnement avant de croire un résultat de test surprenant."
weight: 8
date: 2026-05-20
series: ["skills"]
series_order: 8
tags: ["holy-book"]
---

# 09.03.08&nbsp;—&nbsp;Skill State

> Un seul skill&nbsp;: `question-state`. Interroge l'environnement avant de croire un résultat.

## Le skill

```
input  : un résultat surprenant (« le test fail »)
output : une série de questions sur l'état :
            - sur quel browser tourne-t-on ?
            - quel commit ?
            - le SUT est-il warm ou cold ?
            - le Redis est-il disponible ?
            - quel est le wait-timeout configuré ?
            - quelle est la version du driver ?
            - le ChromeDriver a-t-il son fix password-manager-off ?
            - est-ce un run isolé ou un run en parallèle ?
            - est-ce que d'autres tests touchent les mêmes ressources SUT ?
```

## Approche

`CLAUDE.md`&nbsp;:

> **Don't propagate a previous run's diagnosis without re-deriving it.**
>
> Logs, screenshots, and prior comments describe a _past_ failure. For a _current_ failure, treat them as hypotheses to test, not conclusions to inherit. Re-derive the cause from this run's evidence (current screenshot, current network response, current PHP) before reaching for the previously-tried fix. One extra check is cheap; stacking workarounds on a wrong diagnosis is what ends in a reboot.

→ `question-state` est le **rituel** qui force cette re-dérivation.  
Cela peut aussi être complété par les connaissances de l'environnement&nbsp;:

- Existe-t-il des bouchons&nbsp;?
- Qu'est-ce qui n'est pas _ISO Prod_&nbsp;?
- ...

## Exemple

```
USER : "le test login fail, c'est le BFCache de Chrome ?"
   ↓
CLAUDE (question-state) :
   - On est sur quel navigateur ?  → Chrome
   - Quel test fail ?   → "valid_login" (smoke gate)
   - Le BFCache concerne post_logout_*, pas valid_login → hypothèse rejetée
   - Quel commit ?     → main branch latest
   - Le ChromeDriver password-manager-off est-il actif ? → check create_drivers_pool
   - Le SUT (CURA) est-il "warm" ?
   - Le test a-t-il retry ? → check logs
   - Combien de tries ?  → si > 5, transient ; si 1, vrai defect
   ↓
HYPOTHESE révisée : peut-être A-ENV-2 si l'adapter custom a été supprimé
```

## «&nbsp;_State, not legend_&nbsp;»

On ne croit pas un fail «&nbsp;_parce qu'on l'a déjà vu fail comme ça_&nbsp;».  
On ré-acquiert le state actuel.

Le `CLAUDE.md` détaille pourquoi c'est crucial&nbsp;:

- Les workarounds basés sur des _suppositions_ s'accumulent silencieusement.
- Chaque mauvais diagnostic ajoute de la dette technique.
- À terme&nbsp;: on se retrouve avec une pile de patches qui ne traitent _rien_.

## Discipline transversale

Ce skill est souvent invoqué _au début_ d'une session de debug&nbsp;:

```
USER : "lance review-report"
   ↓
CLAUDE : (review-report identifie le test fail)
   ↓
CLAUDE : "Avant de proposer un fix, je lance question-state..."
   ↓
CLAUDE : (question-state révèle un détail oublié, par exemple le warm-up Heroku qui n'a pas tourné)
   ↓
CLAUDE : "Le fail est probablement A-ENV-1 (dyno cold). Veux-tu relancer avec warm-up ?"
```
