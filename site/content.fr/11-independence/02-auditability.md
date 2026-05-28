---
title: "11.02 — Auditabilité « en une après‑midi »"
description: "L'auditabilité d'Ocarina en une après-midi : un framework lisible de bout en bout, une seule dépendance d'exécution et aucune magie cachée."
weight: 2
date: 2026-05-20
series: ["independance"]
series_order: 2
---

# 11.02&nbsp;—&nbsp;Auditabilité «&nbsp;_en une après‑midi_&nbsp;»

> Engagement opérationnel&nbsp;: un humain doit pouvoir _lire_ tout le framework et le comprendre en quelques heures. Pas de magie cachée.

## Engagement

Citation du Holy Book (chapitre «&nbsp;_Qu'est donc Ocarina&nbsp;?_&nbsp;»)&nbsp;:

> Pour les équipes bloquées par des _politiques de sécurité_&nbsp;: le code est petit, auditable en une après‑midi. Rien de caché. Les seules dépendances externes sont dans les plugins post‑exécution et si l'une d'elles ne passe pas, elle se retire sans que le reste ne casse.

## Le moins de dépendances possible

```toml
dependencies = ["python-docx>=1.2.0"]
```

`python-docx` est utilisé _exclusivement_ par `generate_docx_proof` (plugin post-exécution).  
Le reste du framework ne l'importe nulle part.

| Audit                                                        | Verdict                                                                                             |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Quelles libs sont vendor-shipped avec Ocarina&nbsp;?         | `python-docx` (+ Python stdlib)                                                                     |
| Si l'auditeur ne fait pas confiance à `python-docx`&nbsp;?   | Désactiver le plugin DOCX&nbsp;→&nbsp;tout le reste tourne                                          |
| Y a-t-il des deps cachées dans `requirements-dev.txt`&nbsp;? | Oui (Selenium, allure, mypy, ruff, …) **mais elles ne sont pas embedded dans les binaires release** |
| Combien de SBOM entries pour `pip install ocarina`&nbsp;?    | ~2 (`ocarina` + `python-docx`)                                                                      |

## Rien de caché

L'auditeur peut **tout vérifier**&nbsp;:

1. **Le code source**&nbsp;: public sur GitHub MIT.
2. **La build**&nbsp;: `hatchling` build standard, reproductible.
3. **Les tests**&nbsp;: cram + pytest + mypy plugins + syrupy + hypothesis.
4. **Le rapport Allure**&nbsp;: publié sur GitHub Pages, consultable par tout le monde.
5. **Les CI**&nbsp;: `main_ci.yml`

Pas de&nbsp;:

- Build step propriétaire.
- Téléchargement d'artefacts tiers à l'install.
- Code obfusqué.
- Télémétrie caché.
- API call externe pour autoriser l'usage.

## Code is Law

Cf. [`../01-philosophy/04-citations-and-influences.md`](../01-philosophy/04-citations-and-influences.md)

> Le code se _substitue_ à la Loi. Lessig, 1999, un cri d'alerte. Puis repris par Ethereum, 2015, à l'inverse comme idéal politique.

Pour que «&nbsp;_le code soit la loi_&nbsp;», il faut qu'il soit _lisible_.  
Sinon c'est juste «&nbsp;_la loi est ce qu'on ne comprend pas, mais qui s'exécute_&nbsp;».

Ocarina est explicitement _auditable_, donc _législatif_ au sens noble.

## Portage

Citation du Holy Book&nbsp;:

> Pour les scénarios les plus extrêmes&nbsp;: Ocarina n'a pas besoin d'être installé.
> Il se copie, s'adapte, et tourne.
> Pas de dépendance à auditer.

→ L'auteur affirme qu'on peut littéralement **copier** le dossier `src/ocarina/` dans son projet et l'utiliser comme un sub-package. Aucune install.

Cas d'usage&nbsp;: un client _ultra-paranoïaque_ qui refuse toute install pip. On copie. On adapte. Ça tourne.

## Séparation `dsl/` /&nbsp;`infra/` /&nbsp;`opinionated/`

Cf. [`../02-ocarina/02-module-tree.md`](../02-ocarina/02-module-tree.md)

| Couche                      | Auditer en premier                                                                 |
| --------------------------- | ---------------------------------------------------------------------------------- |
| `railway/`                  | 30 minutes&nbsp;:&nbsp;comprendre ROP                                              |
| `custom_types/`             | 30 minutes&nbsp;:&nbsp;types et alias                                              |
| `dsl/testing_with_railway/` | 1h&nbsp;:&nbsp;la machine à états du DSL                                           |
| `dsl/invariants/`           | 1h&nbsp;:&nbsp;chaîne d'invariants                                                 |
| `dsl/testing/`              | 1h&nbsp;:&nbsp;orchestration (Test&nbsp;→&nbsp;Suite →&nbsp;Campaign →&nbsp;Cycle) |
| `infra/`                    | 30 minutes&nbsp;:&nbsp;pool, builder, screenshotter                                |
| `opinionated/`              | 30 minutes&nbsp;:&nbsp;CLI, loggers, plugins, bootstrap                            |

→ Total&nbsp;: **~5 heures** pour un audit complet. Soit une après-midi calme.

## Plugins post-exécution uniquement

> Les seules dépendances externes sont dans les plugins post‑exécution et si l'une d'elles ne passe pas, elle se retire sans que le reste ne casse.

Cf. [`../02-ocarina/11-opinionated/05-plugins-reports.md`](../02-ocarina/11-opinionated/05-plugins-reports.md) et [`../02-ocarina/11-opinionated/06-bootstrap-launcher.md`](../02-ocarina/11-opinionated/06-bootstrap-launcher.md)

`run_plugins(*plugins, exceptions_logger)`&nbsp;:

```python
def _run_plugin(plugin: Effect, exceptions_logger: ILogger) -> None:
    try:
        plugin()
    except Exception as exc:
        exceptions_logger.exception("The plugin failed.", exc=exc)
```

Si `python-docx` est cassé /&nbsp;non installable&nbsp;: le plugin DOCX lève, on log, **le reste continue**.

Le run produit toujours&nbsp;:

1. Le rapport `pretty_print_results`.
2. Le rapport JSON (`results_to_json`).
3. Le `sys.exit(1)` si fail.

Seul le DOCX manquera.  
Par hygiène, on peut retirer l'appel au plugin DOCX de son fichier `main.py` en tant qu'utilisateur.

## Anti No-Code

Cf. Holy Book (chapitre «&nbsp;_Premiers retours_&nbsp;», section «&nbsp;_Anti No-Code_&nbsp;»)&nbsp;:

> Le code est une donnée brute. Auditable. Consultable. **Une boîte blanche.**
> Très exactement ce avec quoi l'IA sait travailler depuis ses débuts.

→ «&nbsp;_Boîte blanche_&nbsp;»&nbsp;: on _voit_ tout. Pas de boîte noire propriétaire.

L'opposition au No-Code n'est pas idéologiquement gratuite&nbsp;:&nbsp;c'est une revendication d'**auditabilité**. Un workflow No-Code est par définition non-auditable.

## Anti dévs

Holy Book&nbsp;:

> contrairement aux _Chercheurs_, les ingénieurs et leurs amis d'école de commerce s'appuient sur des _vues de l'esprit_.
> Les écoles les plus "prestigieuses" leur ont appris une chose&nbsp;: faire passer le melon pour de "l'ingénierie", là où ceux qui savent qualifient ce travail d'_astrologie de la programmation_.

→ Ocarina rejette le _melon_. Le code est _ce qu'il est_, vérifiable. Pas de «&nbsp;_patterns_&nbsp;» ésotériques qui justifient une complexité stupide.

## Conséquence pour les équipes _bloquées par les politiques de sécurité_

Le pitch de l'auditabilité s'adresse explicitement à elles&nbsp;:

> Pour les équipes bloquées par des _politiques de sécurité_&nbsp;: le code est petit, auditable en une après‑midi.

Une équipe qui n'a pas droit à `pip install <random>` peut&nbsp;:

1. Auditer Ocarina (une après-midi).
2. Auditer les adapters projet (quelques heures de plus).
3. Demander à ce que ce soit whitelist par l'équipe sécurité.
4. Tourner sans crainte.

Pas besoin d'un consultant Ocarina, pas besoin d'un SaaS, pas besoin d'une licence entreprise.  
C'est **libre**.
