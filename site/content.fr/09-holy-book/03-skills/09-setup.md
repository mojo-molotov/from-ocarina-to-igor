---
title: "09.03.09 — Skill Setup"
description: "Le skill Setup exposé aux IA, setup-environment : l'onboarding d'un nouveau contributeur, humain ou IA, sur un projet Ocarina."
weight: 9
date: 2026-05-20
series: ["skills"]
series_order: 9
tags: ["holy-book"]
---

# 09.03.09&nbsp;—&nbsp;Skill Setup

> Un seul skill&nbsp;: `setup-environment`. Onboarding d'un nouveau contributeur (humain ou IA) sur le projet.

## Le skill

```
input  : un repo frais
output : étapes d'onboarding :
            1. venv
            2. pip install (deps dev + ocarina)
            3. ruff / mypy / pre-commit installés
            4. CLAUDE.local.md créé (avec demande paths à l'utilisateur)
            5. smoke-check du runner (un test minimal qui valide que tout marche)
            6. boucle pré-commit testée
```

## Étape 1&nbsp;: venv

```bash
python -m venv .venv
source .venv/bin/activate
```

## Étape 2&nbsp;: pip install

```bash
pip install . ruff mypy mypy-extensions typing-extensions pre-commit
```

## Étape 3&nbsp;: outillage de dev

```bash
pre-commit install --config .pre-commit-config.yaml
```

## Étape 4&nbsp;: `CLAUDE.local.md`

`CLAUDE.local.md` est **gitignored** et contient les paths machine-specifiques.

Le skill `setup-environment`&nbsp;:

1. Vérifie si le fichier existe.
2. Sinon&nbsp;: le crée avec le template du `CLAUDE.md`.
3. **Demande** à l'utilisateur les paths (`chromedriver`, clones des repos de l'écosystème d'Ocarina).
4. Ne devine pas les paths (sauf `find ~/ -name chromedriver -type f 2>/dev/null` qui est documenté comme aide).

`CLAUDE.md`&nbsp;:

> `CLAUDE.local.md` is gitignored and stores per-machine paths. If it's missing, create it with the template below&nbsp;—&nbsp;and ask for the paths, don't guess.

## Étape 5&nbsp;: smoke-check du runner

```bash
python -u src/main.py --browser firefox --driver-path ./geckodriver --workers 3 --only "valid_login"
```

Lance _juste_ un test de fumée. Si ça passe&nbsp;: l'environnement est OK.

Le `--only valid_login` filtre tout le reste. Permet un check rapide plutôt qu'un cycle complet.

## Étape 6&nbsp;: boucle pre-commit

```bash
# faire un edit mineur dans src/
git add src/edited_file.py
git commit -m "test: setup smoke"
```

Le `pre-commit` doit s'exécuter. Si fail&nbsp;: signalé, debug ensemble.  
En mode «&nbsp;_vibe testing_&nbsp;», plus le _pre-commit_ est agressif mieux c'est&nbsp;: l'IA se retrouve dans un contexte proche de ce que l'on appelle l'_apprentissage par renforcement_.

Si le _pre-commit_ a une «&nbsp;_grosse_&nbsp;» batterie, comme par exemple de croiser les vérifications du formatage du code, du lint et du typage systématiquement, l'IA sera bien plus efficace pour se corriger rapidement et ne pourra jamais _commit_ quelque chose de totalement inapproprié (= qui ne «&nbsp;_compile_&nbsp;» même pas).

## Valeur ajoutée

| Sans skill                                                                                                                      | Avec skill                                    |
| ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Le nouveau venu lit le README, fait les étapes _à la main_, se trompe, s'énerve, publie une vidéo YouTube pour insulter Ocarina | Étapes _séquentielles_, vérifiées une par une |
| Pas de check que tout marche vraiment                                                                                           | Smoke-check confirme                          |
| `CLAUDE.local.md` souvent oublié                                                                                                | Le skill force sa création                    |

## «&nbsp;_Onboarding scriptable_&nbsp;»

C'est l'incarnation du principe&nbsp;: un projet doit être _bootstrappable_ en suivant une recette. Pas de savoir tribal, pas de «&nbsp;_ah oui faut faire ça aussi_&nbsp;».

Citations du Holy Book&nbsp;:

> Les étapes d'onboarding (venv, `pip install`, `ruff` /&nbsp;`mypy` /&nbsp;`pre-commit`, smoke-check du runner) vivent dans `setup-environment`.

> Ocarina est **dense, immédiatement opérationnel et strict**. Pensé pour que les humains ainsi que les LLMs en comprennent le cœur et l'usage sans friction.

## Lien avec la philosophie «&nbsp;_auditable en une après-midi_&nbsp;»

Cf. [`../../11-independence/02-auditability.md`](../../11-independence/02-auditability.md)

L'onboarding scriptable est le prélude à l'audit&nbsp;: sans pouvoir _faire tourner_ le projet, on ne peut pas le comprendre.
