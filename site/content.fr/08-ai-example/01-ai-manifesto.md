---
title: "08.01 — Code : 99% Claude, 1% Igor, intelligence : 50-50"
weight: 1
date: 2026-05-20
series: ["ai-example"]
series_order: 1
tags: ["watcher"]
---

# 08.01&nbsp;—&nbsp;Code&nbsp;: 99% Claude, 1% Igor, intelligence&nbsp;: 50-50

## README

> ## A note to the reader
>
> This project is an experiment in AI-driven test engineering. In the interest of honesty about how it was built:
>
> |                  | Claude Code | Human |
> | ---------------- | ----------- | ----- |
> | **Code written** | 99%         | 1%    |
> | **Intelligence** | 50%         | 50%   |
>
> Almost every line was machine-written. The judgement behind it&nbsp;—&nbsp;what to test, what to distrust, when to dig and when to stop&nbsp;—&nbsp;was shared.

## `CLAUDE.md`

`CLAUDE.md` est un _contrat de travail_ avec Claude qui définit&nbsp;:

1. Où vivent les fichiers (layout `src/`).
2. Conventions de code (`TYPE_CHECKING` guard, log factories, etc.).
3. Hard-won rules («&nbsp;_No tricks or hacks_&nbsp;», «&nbsp;_Teach the pattern, not the symptom_&nbsp;», etc.).
4. Patterns approuvés (data-driven, scenario fragments, dispatch tables).
5. Patterns interdits (JS-click pour bypasser, `time.sleep` pour masquer une race condition, etc.).

Ces lignes sont **lues par Claude à chaque session (ouverture d'un "chat")** pour le cadrer.

## `CLAUDE.slim.md`

Version courte du `CLAUDE.md`.  
Mêmes règles, mais sans exemples ni justifications, sans l'expertise&nbsp;: juste les _règles_.

Holy Book (chapitre "Utiliser Ocarina avec l’IA")&nbsp;:

> Slim quand le contexte est chargé&nbsp;; complet pour l'onboarding et les revues. En cas de divergence, le complet l'emporte.

C'est un mécanisme de **gestion de la fenêtre de contexte**&nbsp;: quand Claude doit charger beaucoup d'autres choses (du code, des SFD, etc.), on lui donne `slim.md` pour économiser des tokens.

## Rappel du Holy Book

### Les trois pierres ancestrales

```
1. CLAUDE.md à la racine du projet.
2. skills/ avec un <nom>/SKILL.md par procédure.
3. Règle de vérification : toute affirmation sur le SUT vient d'une observation
   (sonde, gh api, curl -v), jamais d'une inférence.
```

Ce sont les trois piliers d'Ocarina pour implémenter la collaboration humain&nbsp;↔&nbsp;IA.

## `CLAUDE.local.md`

```markdown
# Local machine config

## chromedriver

Path: `/path/to/chromedriver`

## Ocarina source repos (git clones)

- **ocarina**: `/path/to/ocarina`
- **ocarina-example**: `/path/to/ocarina-example`
```

Fichier _gitignored_.

→ Claude doit lire les paths dans `CLAUDE.local.md` plutôt que de les hard-coder ou les chercher.  
Si le fichier manque&nbsp;: Claude doit le créer en posant des questions à l'utilisateur pour être guidé.

## Empirisme

Phrase _rituelle_ citée dans le Holy Book&nbsp;:

> «&nbsp;_Juste remarque, je suppose. Je vérifie empiriquement._&nbsp;»

Avant d'écrire un test basé sur _ce qu'on pense_ que le SUT fait, on **vérifie** via&nbsp;:

1. Une sonde (`write-a-probe` skill).
2. `gh api` pour lire le code source.
3. `curl -v` pour observer la réponse HTTP.

C'est ce qui distingue le projet IA des suites e2e classiques&nbsp;: **on ne suppose pas&nbsp;!**  
On _vérifie_, puis on encode.

## Remonter, ne pas appliquer

Holy Book&nbsp;:

> **Remonter, ne pas appliquer.** Les skills produisent&nbsp;; l'utilisateur décide.

Claude **peut**&nbsp;:

1. Analyser le rapport du dernier run (skill `review-report`).
2. Suggérer une catégorisation des fails (intentional gap /&nbsp;cross-browser /&nbsp;real regression).
3. Proposer une mise à jour de `IDENTIFIED_GAPS.md`.

Mais Claude **ne décide pas**&nbsp;:

1. Quelle catégorie est correcte&nbsp;→&nbsp;l'humain valide.
2. Si un gap doit être ajouté&nbsp;→&nbsp;l'humain confirme.
3. Si on doit modifier la spec&nbsp;→&nbsp;l'humain approuve (le skill `update-frd-and-tests` produit une diff, l'humain merge).

## «&nbsp;_Les tests gap sont reformulés, pas basculés_&nbsp;»

Citation&nbsp;:

> **Les tests gap sont reformulés, pas basculés au vert.** Inverser l'assertion, renommer, déplacer la ligne dans le doc de stratégie, consigner la date dans `IDENTIFIED_GAPS.md`. Le tout via `update-frd-and-tests`.

Si un gap test était rouge (CURA ne valide pas la date) et qu'un jour CURA est patché (la date est maintenant validée), alors&nbsp;:

- ❌ Mauvaise approche&nbsp;: supprimer le test, le mettre en vert, retirer l'assertion.
- ✅ Bonne approche&nbsp;: **garder le test**, **inverser l'assertion** («&nbsp;_on s'attend à ce que la validation marche_&nbsp;»), renommer («&nbsp;_Date validation works_&nbsp;» au lieu de «&nbsp;_Date validation gap_&nbsp;»), mettre à jour `IDENTIFIED_GAPS.md` avec date de fix.

→ L'historique des gaps est **préservé**. Aucune amnésie.

## «&nbsp;_Les signaux des watchers sont négatifs uniquement_&nbsp;»

Citation&nbsp;:

> **Les signaux des watchers sont négatifs uniquement.** Un watcher qui émet «&nbsp;_login réussi_&nbsp;» casse le contrat.

Expliqué ici&nbsp;: [`../02-ocarina/07-watcher.md`](../02-ocarina/07-watcher.md)  
Existe explicitement comme règle de discipline pour Claude.

## «&nbsp;_Distribué quand une ressource est partagée_&nbsp;»

> **Distribué quand une ressource est partagée.** Dès que plusieurs workers se partagent une ressource plafonnée par le SUT (sessions, créneaux, quotas), la coordination passe par des primitives distribuées. Sinon, un cache local en mémoire suffit&nbsp;—&nbsp;à condition que les clés soient garanties uniques et que leur génération soit thread-safe.

C'est ce qu'incarne `ocarina-example` (cf. [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md))&nbsp;: `dogpile.cache.memory` _ou_ Redis selon la portée.

## «&nbsp;_mtime, pas nom de fichier_&nbsp;»

> **Mtime, pas nom de fichier.** Les suffixes UUID sont aléatoires&nbsp;; `pick-*` trie par mtime.

C'est-à-dire&nbsp;: pour _piocher_ le dernier rapport /&nbsp;log /&nbsp;screenshot, on _ne_ trie _pas_ par nom (les UUIDs sont aléatoires). On trie par mtime (date de modif).

Tous les skills `pick-screenshots`, `pick-logs`, `pick-reports` suivent cette convention.

## Discipline

L'enjeu&nbsp;: éviter que Claude n'_hallucine_.  
Les règles ci-dessus sont des **contre-poids cognitifs** pour la machine.

Sans elles, l'IA serait tentée&nbsp;:

1. D'inventer un test au lieu de vérifier le SUT.
2. De masquer une régression en mettant le test au vert.
3. De suggérer un watcher positif («&nbsp;_login réussi_&nbsp;») pour avoir l'air rassurant.
4. D'utiliser un cache local pour un quota distribué.
5. De consommer énormément de tokens en navigant péniblement dans les screenshots, logs et rapports.

`CLAUDE.md` est un _système immunitaire_.
