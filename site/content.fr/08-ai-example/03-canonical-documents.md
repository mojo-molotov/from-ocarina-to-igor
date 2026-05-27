---
title: "08.03 — Documentation"
description: "Le projet IA est le plus documenté de l'écosystème d'Ocarina."
weight: 3
date: 2026-05-20
series: ["ai-example"]
series_order: 3
---

# 08.03&nbsp;—&nbsp;Documentation

> Le projet IA est le plus documenté de l'écosystème d'Ocarina.

## Listing

| Document                | Statut                             | Lectorat                   |
| ----------------------- | ---------------------------------- | -------------------------- |
| `CLAUDE.md`             | Contrat de travail Claude ↔ projet | Claude + tout contributeur |
| `CURA_FRD.md`           | Spec reconstruite                  | Mainteneurs, stakeholders  |
| `CURA_TEST_STRATEGY.md` | Stratégie de test                  | Mainteneurs                |
| `IDENTIFIED_GAPS.md`    | Inventaire technique des gaps      | Mainteneurs                |

## `CLAUDE.md`

1. **Key documents**&nbsp;: pointe vers `README.md`, `CURA_FRD.md`, `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md`, `CLAUDE.local.md`.
2. **Project**&nbsp;: 2 phrases sur le projet (CURA, Python 3.14+, demo creds).
3. **Project philosophy**&nbsp;: «&nbsp;_No tricks or hacks. Teach the pattern, not the symptom._&nbsp;»
4. **`CLAUDE.local.md` template**&nbsp;: ce que doit contenir le fichier gitignored.
5. **Layout**&nbsp;: arbre `src/` complet, audité (commande shell qui vérifie que `CLAUDE.md` et l'arbre réel sont synchronisés).
6. **Ocarina hierarchy**&nbsp;: rappel `Test → Suite → Campaign → Cycle`.
7. **Test strategy**&nbsp;: structure du cycle, smoke gate, taxonomie.
8. **Running tests**&nbsp;: commandes CLI.
9. **Reports and screenshots**&nbsp;: règle «&nbsp;un screenshot par drive_page&nbsp;».
10. **Scenario fragments**&nbsp;: quand extraire un fragment.
11. **Data-driven tests**&nbsp;: quand utiliser le pattern, conventions de naming.
12. **Mixins partagés**&nbsp;: `SeleniumBackAndForwardNavigationMixin`.
13. **Conventions**&nbsp;: 12 règles concrètes (TYPE_CHECKING guard, log factories, etc.).
14. **Hard-won rules**&nbsp;: règles tirées de l'expérience, avec exemples du passé.

## Hard-won rules

### «&nbsp;_Verify SUT behaviour&nbsp;—&nbsp;don't theorise_&nbsp;»

> CURA is open source. Before building on a server-side claim, read the PHP:
>
> ```bash
> gh api repos/katalon-studio/katalon-demo-cura/contents/<file>.php --jq '.content' | base64 -d
> ```

→ Pas d'inférence. C'est à l'humain d'être «&nbsp;_assertif_&nbsp;».

### «&nbsp;_Inspect the SUT for security /&nbsp;spec gaps_&nbsp;»

> This is the **encouraged** use of source inspection.

→ Lecture du code _encouragée_ pour trouver des gaps.

### «&nbsp;_Security testing is functional and static&nbsp;—&nbsp;never active_&nbsp;»

> **Forbidden, no exceptions:**
>
> - Crafted attack payloads of any kind: SQL injection strings, XSS /&nbsp;HTML /&nbsp;JS payloads, command injection, header/parameter pollution, path traversal, deserialisation payloads.
> - Token tampering, signature stripping, cookie forgery, session-fixation attempts, forced-browsing fuzzers.
> - Cross-origin POSTs constructed outside the suite, scripted directory enumeration, DOS, rate-floods.

→ Tests de sécurité **fonctionnels** uniquement («&nbsp;_utiliser l'app comme un utilisateur_&nbsp;»), jamais _actifs_ («&nbsp;_attaquer l'app comme un adversaire [acteur malveillant]_&nbsp;»).

### «&nbsp;_Throwaway probes&nbsp;—&nbsp;when source-reading and the suite don't agree_&nbsp;»

> A **probe** is a one-off script that drives the browser (or raw HTTP) through a suspect flow and prints concrete runtime state. It **bypasses the Ocarina workflow entirely**&nbsp;—&nbsp;no `create_selenium_test`, no suites, no campaigns, no assertions. Probes live in a gitignored directory, are **never committed or pushed**, and are deleted once the answer lands in a durable artifact.

→ On _peut_ écrire un script **jetable** pour explorer, mais **on ne le commit jamais**. Une trouvaille atterrit dans un artefact (gap, SFD update, test).

### «&nbsp;A probe must exercise the _exact_ target the code under test will use&nbsp;»

> "Exact target" means **all** of: exact locator, exact screen /&nbsp;page state, exact wait condition, exact action.

→ Une sonde sur _autre chose_ ne prouve _rien_ pour ce qui est à tester&nbsp;: c'est de l'_empirisme_. **On fait et on refait.**

### «&nbsp;_Probe sequences vs ritual workarounds&nbsp;—&nbsp;multi-action "dances"_&nbsp;»

> **Probe sequence (legitimate).** The dance _is_ the test.
> **Ritual workaround (not legitimate).** Glue around a _hypothesis_ about SUT behaviour.

→ Une séquence d'actions peut être _le test_ ou _une solution de contournement_. Si on enlève une étape et que le test change _ce qu'il teste_&nbsp;→&nbsp;sonde. Sinon (juste «&nbsp;_pour que ça marche_&nbsp;»)&nbsp;→&nbsp;solution de contournement à éliminer.

### «&nbsp;_A cross-browser behavioural difference is a finding, not a test to route around_&nbsp;»

> **Never skip a test on the browser where it fails.**

→ Si un test fail sur Chrome mais passe sur Firefox&nbsp;→&nbsp;**il s'agit d'une trouvaille**, à documenter et à _garder en tant que test en échec_ sur Chrome. Pas à skipper.

### «&nbsp;_Functional testing simulates a real human&nbsp;—&nbsp;ask "would a real person hit this?"_&nbsp;»

> Every test here stands in for a person clicking through CURA in a browser.

→ Un test automatisé = une simulation du parcours d'un humain. Si le test échoue mais qu'un humain réussirait dans les mêmes conditions&nbsp;→&nbsp;**le problème vient du test**. Sinon&nbsp;→&nbsp;c'est une _anomalie_.

### «&nbsp;_Confirming a back-forward-cache exposure&nbsp;—&nbsp;the back-then-reload check_&nbsp;»

→ Recette précise pour **confirmer un problème avec le BFCache**&nbsp;: `back()` puis `refresh()`&nbsp;; si `back()` affiche une page qu'il ne devrait pas, sans redirection, mais qu'on est tout de même redirigé après un `refresh()`&nbsp;→&nbsp;BFCache hit, anomalie.

### «&nbsp;_Scenario file structure_&nbsp;»

> **One scenario per file.** (...)
> **Top docstring gives the flow as arrows.** A reader must know exactly what the file exercises before reading any code.

→ Discipline de structure. Un docstring en flèches (`open → fill → submit → verify`) en haut de chaque fichier de test. Un fichier de test par scénario de test.

### «&nbsp;_POM selectors live at the top of the class_&nbsp;»

→ Tous les sélecteurs sont groupés en haut de leur POM respectif. **On ne les disperse pas.**

### «&nbsp;Always use WebDriverWait&nbsp;—&nbsp;never raw find_element&nbsp;»

→ Tableau précis de quel `expected_conditions` utiliser pour quel cas avec Selenium.  
Ne pas utiliser `find_element` directement.

### «&nbsp;_Widget-decorated inputs: drive the widget's API, don't fight its intercepts_&nbsp;»

→ Pour les datepickers par exemple&nbsp;:&nbsp;contourner les sorcelleries UX/UI du composant web, interagir via JS, appeler l'API du composant. Exemple cité&nbsp;: `AppointmentPage.enter_visit_date` (Bootstrap 3 datepicker).

### «&nbsp;_Setup/teardown actions: prefer the URL, save the UI click for the test that owns it_&nbsp;»

→ Utiliser le chemin le plus direct pour préparer un test (URL, API, session injectée, fixtures). Ne faire des clics sur l'interface utilisateur que si le test vérifie réellement cette interface utilisateur.

## `CURA_FRD.md`

1. Executive Summary
2. System Overview (purpose, stakeholders, deployment)
3. User Roles & Personas (authenticated, unauthenticated, demo)
4. **Functional Requirements** (Auth, Appointment, History, Profile)&nbsp;—&nbsp;c'est le cœur
5. Element IDs (DOM selectors)
6. URL map
7. Business rules
8. Error handling
9. **Known bugs /&nbsp;gaps** (§9.1 à §9.11)

C'est une documentation **reconstruite** par IA afin de rendre vérifiable le travail qui a été co-construit.

## `CURA_TEST_STRATEGY.md`

1. Scope (functional e2e, out: perf/accessibility/email/etc.)
2. Test objectives
3. **Test types**&nbsp;: happy /&nbsp;unhappy /&nbsp;edge /&nbsp;**business attack** /&nbsp;exploratory /&nbsp;**permanent security regression**
4. Coverage tables (REQ-AUTH-N × test_X)
5. Suite/campaign tree
6. Expected pass/fail breakdown
7. **Categories of results** (cf. README&nbsp;: intentional gap, cross-browser, real regression, transient)
8. Run notes

## `IDENTIFIED_GAPS.md`

| ID          | Catégorie     | Sujet                                                                                                                                                                                                              |
| ----------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| G-SEC-1     | Sécurité      | Pas de jeton CSRF sur les formulaires                                                                                                                                                                              |
| G-SEC-2     | Sécurité      | `_f::logout()` ne détruit pas le cookie                                                                                                                                                                            |
| G-SEC-3     | Sécurité      | `===` strict mais pas de rate-limit/lockout/captcha                                                                                                                                                                |
| G-DATA-1    | Données       | Pas de validation serveur de visit_date                                                                                                                                                                            |
| G-DATA-2    | Données       | Pas de contraintes d'unicité sur les rendez-vous, ni de vérifications de conflits                                                                                                                                  |
| G-SPEC-1    | Spec          | L'historique des réservations est trié par ordre de prise de rendez-vous, pas par la date des rendez-vous sur la page pour les consulter                                                                           |
| G-SPEC-2    | Spec          | Page de profil présente mais vide                                                                                                                                                                                  |
| G-SPEC-3    | Spec          | Une tentative d'accès non autorisé redirige sur la page d'accueil, pas sur la page de connexion                                                                                                                    |
| B-BROWSER-1 | Browser       | Anomalie due au BFCache&nbsp;: on peut faire réapparaître des pages protégées après déconnexion en utilisant le bouton "précédent"                                                                                 |
| A-ENV-1     | Environnement | Problème d'environnement avec les requêtes POST lorsqu'on stresse avec plusieurs workers (3)                                                                                                                       |
| A-ENV-2     | Environnement | Problème d'environnement de test&nbsp;: Chrome affiche une modale indésirable en plein test à cause de la fragilité du mot de passe de démo (résolu en désactivant la fonctionnalité dans l'environnement de test) |

- **Where**&nbsp;: file:line du PHP responsable.
- **Symptom**&nbsp;: ce qu'on observe.
- **GitHub source vs deployment**&nbsp;: la différence éventuelle.
- **Bonus bug** (si présent)&nbsp;: variantes /&nbsp;bugs en cascade.
- **Impact**&nbsp;: conséquences exploitables.
- **Test(s)**&nbsp;: nom des tests qui matérialisent.
- **SFD ref**&nbsp;: pointeur vers `§9.X`.

→ Format **forensique standard**. Tout est vérifiable.
