---
title: "12.15 — Typage, ISTQB, Reinforcement Learning, probes : pourquoi l'IA marche dans Ocarina"
description: "Pourquoi l'IA fonctionne dans Ocarina : typage strict, alignement ISTQB et probes, un mécanisme emprunté au Reinforcement Learning, contrainte plus récompense."
weight: 15
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 15
tags: ["rop", "istqb", "typage"]
---

# 12.15&nbsp;—&nbsp;Typage, ISTQB, Reinforcement Learning, _probes_&nbsp;: pourquoi l'IA marche dans Ocarina

> Pourquoi tant d'**obsession** pour le typage strict, la formalisation de chaque interface, l'alignement sur l'**ISTQB**, le refus d'exécuter une assertion sans avoir _observé_&nbsp;? Le mécanisme est emprunté au **Reinforcement Learning**&nbsp;:&nbsp;un agent ne progresse que sous **contrainte**&nbsp;+&nbsp;**signal de récompense**.

## 1. Un LLM nu n'est qu'un mauvais collaborateur

Un LLM sans environnement structuré est&nbsp;:

- _Optimiste_, il suppose que son code marche.
- _Persuasif_, son _output_ est convaincant même quand il est faux.
- _Sans mémoire_, il oublie les conventions entre sessions.
- _Sans feedback_, il n'a aucun moyen de savoir qu'il s'est trompé.
- _Aime ce qu'il juge comme étant «&nbsp;le plus probable&nbsp;»_, il tend vers les patterns _populaires_, pas vers les patterns _corrects_.

**Sans environnement, un LLM est un développeur junior en surconfiance** qui produit du code qui _ressemble_ au bon, casse en prod, et n'apprend rien de l'échec.

## 2. Reconstruire une _feedback loop_

| Signal                            | Effet                                                | Outil Ocarina                                                       |
| --------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------- |
| **Negative feedback** rapide      | «&nbsp;_Ce que tu viens de produire est faux_&nbsp;» | **mypy strict**, erreurs algébriques, runtime probes, `Result.Fail` |
| **Positive convention** explicite | «&nbsp;_Voici ce qu'il faut faire_&nbsp;»            | **ISTQB vocabulary**, `CLAUDE.md`, _skills_ versionnées             |

C'est une **boucle de Reinforcement Learning**.

## 3. Le _Reinforcement Learning_ comme cadre théorique

### Origines

| Année | Contribution                                                            | Auteur(s)                                      |
| ----- | ----------------------------------------------------------------------- | ---------------------------------------------- |
| 1948  | **Cybernétique**, contrôle par feedback                                 | Norbert Wiener                                 |
| 1957  | **Dynamic Programming**                                                 | Richard Bellman                                |
| 1989  | **Q-learning**&nbsp;—&nbsp;RL tabulaire (article de revue&nbsp;: 1992)  | Chris Watkins                                  |
| 1992  | **REINFORCE**&nbsp;—&nbsp;policy gradient                               | Ronald Williams                                |
| 1998  | Livre canonique «&nbsp;_Reinforcement Learning: An Introduction_&nbsp;» | Sutton & Barto                                 |
| 2013  | **DQN**&nbsp;—&nbsp;Deep Q-Network sur Atari                            | Mnih, _et al._ (DeepMind)                      |
| 2016  | **AlphaGo** bat Lee Sedol                                               | DeepMind                                       |
| 2017  | **PPO**&nbsp;—&nbsp;Proximal Policy Optimization                        | Schulman, _et al._ (OpenAI)                    |
| 2017  | **RLHF**&nbsp;—&nbsp;RL from Human Preferences                          | Christiano, Leike, Brown, Martic, Legg, Amodei |
| 2022  | **InstructGPT**&nbsp;→&nbsp;ChatGPT                                     | OpenAI                                         |
| 2022  | **Constitutional AI** (CAI)                                             | Anthropic&nbsp;—&nbsp;Bai _et al._             |

### Bases du RL

```
   ┌─────────────┐    action     ┌─────────────┐
   │             │──────────────>│             │
   │   AGENT     │               │ ENVIRONMENT │
   │             │<──────────────│             │
   └─────────────┘    state +    └─────────────┘
                      reward
```

- **État** (`state`)&nbsp;:&nbsp;ce que voit l'agent.
- **Action** (`action`)&nbsp;:&nbsp;ce qu'il choisit de faire.
- **Récompense** (`reward`)&nbsp;:&nbsp;signal qui dit si c'est bon.
- **Policy** (`π`)&nbsp;:&nbsp;la stratégie de l'agent, comment il choisit son action.

Avec le RL, l'agent apprend en **explorant** l'espace des actions et en **renforçant** les actions qui amènent à une meilleure récompense.

### Analogie

| RL classique     | LLM dans Ocarina                                                                        |
| ---------------- | --------------------------------------------------------------------------------------- |
| Espace d'actions | Tous les caractères /&nbsp;tokens possibles                                             |
| État             | Le prompt +&nbsp;ce que le LLM a déjà répondu (la _sortie partielle_)                   |
| Reward différé   | mypy vert, tests correspondent à l'attendu, PR mergées                                  |
| Episode          | Une session de dév                                                                      |
| Policy           | Distribution sur les tokens conditionnée au contexte (poids +&nbsp;prompt +&nbsp;tools) |

Ce qui distingue un LLM _utile_ d'un LLM qui hallucine, c'est la **densité du signal de reward**.  
Plus le signal est rapide et précis, plus l'agent _converge_ vers les bons patterns.

## 4. Typage strict comme signal RL

`mypy --strict` est un **signal de reward immédiat**&nbsp;:

```
+----------------+
| LLM produit    | <─────────────────────────────────────────────────┐
| code Python    |                                                   │
+--------+-------+                                                   │
         │                                                           │
         v                                                           │
+----------------+                                                   │
| mypy strict    |   <- reward signal binaire                        │
| tourne en      |      pass / fail                                  │
| < 5 secondes   |      enrichi avec des erreurs de types formelles  │
+--------+-------+                                                   │
         │                                                           │
         v                                                           │
   FAIL ─┤───── relit l'erreur, corrige ─────────────────────────────┤
         │                                                           │
   PASS ─┴───── continue ────────────────────────────────────────────┘
                   │
                   v
                 livre
```

| pytest only                                        | mypy strict                                              |
| -------------------------------------------------- | -------------------------------------------------------- |
| Code lancé en prod                                 | Erreur attrapée à l'analyse statique                     |
| Reward arrive quand c'est déjà trop tard (prod/CI) | Reward arrive en _secondes_ depuis l'environnement local |
| Reward est _flaky_ (test aléatoire)                | Reward est _déterministe_                                |
| L'agent ne sait pas _quoi_ corriger                | L'erreur mypy pointe la ligne exacte                     |
| Apprend à _surmonter_ les flakes                   | Apprend la _grammaire correcte_                          |

`mypy --strict` est donc ici, dans la grille RL, **le reward signal le plus efficace possible pour un LLM dév Python**.

## 5. ISTQB comme contrainte de l'_action space_

L'**ISTQB** (_International Software Testing Qualifications Board_) standardise le _vocabulaire de test_.

Ocarina **mappe 1:1** cette hiérarchie dans son code&nbsp;:

| ISTQB         | Ocarina (classe) |
| ------------- | ---------------- |
| Test Step     | `act` (callable) |
| Test Case     | `Test`           |
| Test Suite    | `TestSuite`      |
| Test Campaign | `TestCampaign`   |
| Test Cycle    | `TestCycle`      |

> **Note (_Test Step_)&nbsp;:** Dans le glossaire ISTQB, le _test step_ n'est pas un niveau hiérarchique autonome mais une composante interne d'un _Test Case_ (la séquence d'actions à exécuter). Ocarina l'implémente bien tel quel (`act`).

> **Note (_Test Campaign_)&nbsp;:** Le terme n'est pas formellement défini dans le glossaire officiel ISTQB, contrairement aux quatre autres. Il est néanmoins d'usage courant et immédiatement compris par les professionnels du test&nbsp;; on le retrouve notamment dans ISO 29119 et dans la plupart des outils de gestion de tests (Xray, TestRail, Zephyr). Son inclusion ici relève du vocabulaire métier partagé plutôt que de la terminologie ISTQB stricto sensu.

- L'_action space_ est **fini, nommé, documenté**.
- Le prompt «&nbsp;_génère une suite de test pour la feature X_&nbsp;» est **non ambigu**.
- Sans ISTQB, le prompt équivalent pytest serait&nbsp;:&nbsp;«&nbsp;génère un module avec des fonctions `test_*` dans le bon répertoire, avec les bonnes fixtures dans `conftest.py`, dans le bon scope, en respectant les markers&nbsp;», _que des décisions implicites, donc que des occasions d'halluciner_.

Avec ISTQB, une seule décision&nbsp;: _quels tests mettre dedans_. L'_action space_ est passé de **plusieurs centaines de décisions** à **une**.

C'est, en RL, **la réduction de l'espace d'exploration par injection de _domain knowledge_**.

## 6. Pourquoi «&nbsp;_branché formellement_&nbsp;» partout

Ocarina ne laisse **aucun trou** dans le typage&nbsp;:

- `Result[T]` est paramétré&nbsp;→&nbsp;on sait toujours quel `T` est en cours.
- `ChainRunner[T]` aussi.
- Les hooks sont des `Callable` avec signature explicite.
- ...

**Aucune décision implicite**.  
Quand un LLM lit le code, il **ne peut pas** se tromper sur le type attendu&nbsp;: il y a une seule réponse possible, dictée par le _type checker_.

C'est ce qu'on appelle, en _design de types_, **«&nbsp;_making illegal states unrepresentable_&nbsp;»** (Yaron Minsky, Jane Street). Ocarina applique ce principe systématiquement.

## 7. Pourquoi ne pas exécuter quand un jeu de données est généré par l'IA

Cas concret. Un LLM produit&nbsp;:

```python
# Pseudo code (not Ocarina)
def test_login_succeeds():
    user = "'; DROP TABLE users; --"
    password = "lol"

    open_login_page()
    fill(user, password)
    click_submit()

    assert current_url() == "/dashboard"
```

C'est le résultat d'une attaque par _prompt injection_ /&nbsp;_data poisoning_&nbsp;:&nbsp;le LLM ne devrait pas faire ça.  
Si ces données atteignent l'exécution&nbsp;:

- Le champ `user` contient une _payload_ SQL.
- L'application cible est compromise, pas testée fonctionnellement.
- L'agent a produit une attaque, pas un test. **C'est interdit.**

### Empirique d'abord

**Empirique**&nbsp;:&nbsp;on _observe_ ce qui est sur la page **avant** de décider.  
Les **probes** _lisent_ la page et dressent des constats **avant** de formaliser l'implémentation d'un test&nbsp;:

L'_information_ rendue est riche. L'agent _apprend_ quelque chose à chaque échec.

### Assertif après

Une fois qu'on _sait_ qu'on est sur le bon _state_, on peut **affirmer**&nbsp;:

```python
# Pseudo code (not Ocarina)
def assert_dashboard_loaded(driver: Driver) -> Result[None]:
    welcome = driver.find_element(By.CSS, ".welcome")
    if welcome.text == "Welcome, John":
        return Ok(None)
    return Fail(Reason.bad_welcome_text(welcome.text))
```

C'est la **séquence d'Ocarina**&nbsp;:

```
        ┌─────────────────────────────────────────────┐
        │ 1. PROBE : qu'est-ce que je vois ?          │
        └────────────────────┬────────────────────────┘
                             v
        ┌─────────────────────────────────────────────┐
        │ 2. DECIDE : selon l'état, quelle action ?   │
        └────────────────────┬────────────────────────┘
                             v
        ┌─────────────────────────────────────────────┐
        │ 3. ACT : exécuter l'action choisie          │
        └────────────────────┬────────────────────────┘
                             v
        ┌─────────────────────────────────────────────┐
        │ 4. ASSERT : vérifier l'invariant final      │
        └─────────────────────────────────────────────┘
```

Comparée à la séquence _assertive-only_&nbsp;:

```
        ┌────────────────────────────┐
        │ ACT : fais ce que tu crois │
        └──────────────┬─────────────┘
                       v
        ┌────────────────────────────┐
        │ ASSERT : explose           │
        └────────────────────────────┘
```

L'IA marche **bien** avec la première, **mal** avec la deuxième.  
La philosophie d'Ocarina est **mathématiquement compatible** avec ce que le RL nous enseigne sur l'apprentissage&nbsp;:&nbsp;pas de comportement appris sans _état observé_.

## 8. Récap.

| Choix Ocarina             | Conséquence pour l'IA                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `mypy --strict`           | Reward signal en < 5s, déterministe, ligne précise                                                           |
| ROP (`Result[T]`)         | Force le LLM à _gérer_ l'erreur                                                                              |
| ISTQB                     | _Action space_ petit, non-ambigu                                                                             |
| Pas d'`async`             | Fuck you                                                                                                     |
| Pas de plugin pytest      | Une seule grammaire, pas de fixtures mystiques qui se métamorphosent en toutes les implémentations possibles |
| Probes obligatoires       | Le LLM procède à l'_observation_ avant l'_affirmation_                                                       |
| Hooks typés               | Pas d'effet de bord caché                                                                                    |
| `CLAUDE.md` /&nbsp;skills | Mémoire externalisée, conventions explicites                                                                 |
| `llms.txt`                | Index lisible par l'IA en un coup de prompt                                                                  |
| MIT, 1 dep                | Auditable par le LLM                                                                                         |

## 9. Lectures connexes

- [`14-real-ai-in-ocarina.md`](14-real-ai-in-ocarina.md)&nbsp;—&nbsp;ce qu'est l'IA, ce qu'Ocarina lui expose.
- [`13-lambda-calculus-rop-origins.md`](13-lambda-calculus-rop-origins.md)&nbsp;—&nbsp;la théorie typique qui sous-tend le DSL.
- [`../02-ocarina/03-railway/`](../02-ocarina/03-railway/README.md)&nbsp;—&nbsp;l'implémentation ROP concrète.
- [`../02-ocarina/06-scenario.md`](../02-ocarina/06-scenario.md)&nbsp;—&nbsp;`drive_page` et `match_page` détaillés.
- [`../08-ai-example/`](../08-ai-example/README.md)&nbsp;—&nbsp;la suite IA + ses _hard-won rules_.
