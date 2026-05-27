---
title: "09.03.07 — Skills Refactor"
description: "Skills qui refactor la base de tests automatisés existante."
weight: 7
date: 2026-05-20
series: ["skills"]
series_order: 7
tags: ["holy-book", "scenarios"]
---

# 09.03.07&nbsp;—&nbsp;Skills Refactor

> Skills qui **refactor** la base de tests automatisés existante.

## Listing (potentiellement non exhaustif)

| Skill                    | Cible                                                                   |
| ------------------------ | ----------------------------------------------------------------------- |
| `refactor-fragmentation` | DRY selon préférence utilisateur                                        |
| `introduce-pom-retries`  | Retries internes aux POMs, avec dédoublement (first-try + with-retries) |

## `refactor-fragmentation`

```
input  : la base de tests
output : suggestions de refactor DRY :
            - blocs répétés dans 3+ scénarios → extract en fragment
            - connectors quasi-identiques → extract un connector paramétré
            - séquences de log+screenshot répétées → extract un helper
         + recommandation au cas par cas
```

`CLAUDE.md`&nbsp;:

> **When to extract a fragment**
>
> - **Don't extract preemptively.** Two scenarios sharing 3 acts is a coincidence. Wait for **3+ scenarios** with the same block.
> - **The block must be a precondition/postcondition, not the focus of any test.** `valid_login.py` does not use the login fragment&nbsp;—&nbsp;login _is_ the test there, and uses `log_and_screenshot` for the meaningful page transition.
> - **Unhappy-path login tests stay self-contained.** `failed_logins` and `unauthenticated_history_access` don't use the fragment&nbsp;—&nbsp;they must stay independent of demo-user state.

1. **Quantité**&nbsp;: 3+ scénarios avec le même bloc.
2. **Rôle**&nbsp;: pré/postcondition, pas le focus du test.
3. **Indépendance**&nbsp;: tests unhappy-path doivent rester self-contained.

`refactor-fragmentation` applique ces critères et **suggère** (sans appliquer).

## `introduce-pom-retries`

```
input  : un connector qui exerce une action flaky (par exemple click un bouton qui peut fail intermittemment)
output : refactor en :
            1. méthode POM `<action>` sans retry (single try)
            2. méthode POM `<action>_with_retries(retries: int, logger: ILogger)` qui retry intern
            3. connectors duaux :
                - `<action>` : appelle POM `<action>`
                - `<action>_with_retries(retries, logger)` : appelle POM `<action>_with_retries`
            4. scénarios mis à jour pour utiliser la variante appropriée
```

C'est ce pattern qu'on voit dans `ocarina-example/lib/connectors/test_steps/actions/dashboard_login.py`&nbsp;:

```python
def login_without_otp(creds: ImmutableCredentials):
    def unwrapped(p: DashboardLoginPage) -> DashboardLoginPage:
        return p.login_without_otp(creds)
    return unwrapped


def login_without_otp_and_with_retries(
    creds: ImmutableCredentials, retries: int, *, logger: ILogger
):
    def unwrapped(p: DashboardLoginPage) -> DashboardLoginPage:
        return p.login_without_otp_and_with_retries(creds, retries, logger=logger)
    return unwrapped
```

Deux connectors. Le scénario choisit selon le besoin&nbsp;:

- Cas happy path&nbsp;: `login_without_otp_and_with_retries` (le `useAuth` à 10% de raté force le retry).
- Cas unhappy path («&nbsp;_login avec mauvais mdp_&nbsp;»)&nbsp;: `login_without_otp` (on _veut_ que l'échec se voie, sans retry).

## Pourquoi dédoubler

| Sans dédoublement                                   | Avec dédoublement                                                                                                                                                     |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Une seule méthode `login(...)`, toujours avec retry | Les tests qui veulent voir un fail immédiat sont brouillés par les retries                                                                                            |
| Pas de différenciation happy /&nbsp;unhappy         | Différenciation claire                                                                                                                                                |
| Tests fragiles si on enlève le retry                | Tests robustes&nbsp;: la couverture de test est préservée, un test complémentaire visant à ne pas tolérer la _flakiness_ permet de continuer de la tracer sur le côté |

## «&nbsp;_Retries au POM, pas au scénario_&nbsp;»

Holy Book (chapitre «&nbsp;_Premiers obstacles du monde réel_&nbsp;»)&nbsp;:

> ## Aléas de pas de test
>
> Pensant avoir laissé derrière moi ce genre de désagréments, j'ai changé de crémerie… pour y découvrir des formulaires instables et des systèmes d'authentification qui fonctionnaient une fois sur deux.
>
> Face à cela, la réponse d'Ocarina est différente&nbsp;: on délègue la responsabilité au POM.

| Variante                                | Avantage                                                                  | Inconvénient                                     |
| --------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------ |
| Retry au framework (`transient_errors`) | Transparent, approprié en cas de _flakiness_ impossible à vraiment isoler | Re-joue _tout_ le test, pas juste l'action flaky |
| Retry au niveau du POM                  | Granulaire + placé dans une méthode bien nommée                           | &nbsp;—&nbsp;                                    |

## Discipline transversale

- **Analyser** des patterns dans la base.
- **Suggérer** des refactors.
- **Ne pas immédiatement appliquer** sauf si instruction explicite.
- **Respecter** les règles d'extraction.
