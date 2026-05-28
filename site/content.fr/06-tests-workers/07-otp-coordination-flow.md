---
title: "06.07 — Flux de coordination OTP + l'anti-précision volontaire"
description: "Le flux de coordination OTP de tests-workers : comment N workers parallèles d'Ocarina récupèrent le bon OTP malgré l'imprécision volontaire."
weight: 7
date: 2026-05-20
series: ["tests-workers"]
series_order: 7
tags: ["otp", "parallelisation"]
---

# 06.07&nbsp;—&nbsp;Flux de coordination OTP + l'imprécision volontaire

> La raison d'être du backend&nbsp;: permettre à N workers parallèles d'Ocarina de **récupérer le bon OTP** pour leur _user_, même quand plusieurs OTP sont générés.

## Flux

```
   ┌───────────────────────────────────────────────────────────────────┐
   │               Worker (parmi --workers 3 d'Ocarina)                │
   └───────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium ouvre la page de connexion au Dashboard                  │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Acquisition du lock distribué Redis (OTP_SEND_LOCK_KEY)           │
   │   → seul ce worker peut cliquer "Send OTP" pendant ACQ            │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ min_utc_date = datetime.now(UTC)                                  │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Cache L1 : enregistre min_utc_date + username dans le cache       │
   │   (clés réservées par reserve_free_cache_key)                     │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium tape username + password + cocher OTP + click "REQ OTP"  │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ IGORISTAN UI : fetch /api/otp?_user=<username>                    │
   │   (x-api-key tapé par Selenium dans l'UI)                         │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ TESTS-WORKERS /api/otp :                                          │
   │   generate(secret) → otpCode                                      │
   │   createdAt = floor(now/1000)*1000  ← amputation ms               │
   │   event = { _user, otpCode, createdAt, expiresAt, ... }           │
   │   redis.set("otp:<now>:<uuid>", JSON, EX 360)                     │
   │   return event                                                    │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ IGORISTAN UI : affiche écran OTP                                  │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Release du lock Redis OTP_SEND_LOCK_KEY                           │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium : retrieve_dashboard_otp_code(min_utc_date, _user)       │
   │   ↓                                                               │
   │   GET /api/otp-history  (x-api-key = IGOR_API_KEY)                │
   │   ↓                                                               │
   │   TESTS-WORKERS : SCAN otp:* + MGET → all events                  │
   │   ↓                                                               │
   │   filtre côté client par _user                                    │
   │   filtre createdAt >= min_utc_date - 1s                           │
   │   tri ASC sur createdAt                                           │
   │   return first.otpCode                                            │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium tape l'OTP dans l'UI Igoristan                           │
   │   → AUTHENTICATED_WITH_MFA                                        │
   └───────────────────────────────────────────────────────────────────┘
```

## Races conditions

1. Worker A&nbsp;: `min_utc_date_A = 13:27:53.123`, génère OTP_A à 13:27:53.250.
2. Worker B&nbsp;: `min_utc_date_B = 13:27:53.130`, génère OTP_B à 13:27:53.470.

Sans coordination, A pourrait récupérer OTP*B (au lieu de OTP_A) parce que les timestamps sont \_très proches* (et tronqués à la seconde près).

## Lock distribué

Le lock `OTP_SEND_LOCK_KEY` _sérialise_ les `REQ OTP` _par user_.  
A fini son `REQ OTP` _avant_ que B commence le sien.

Mais&nbsp;: si deux users différents (U, U') demandent OTP _simultanément_, ils ne se _bloquent pas_ entre eux (lock par user). Les deux OTP arrivent à la même seconde. C'est ici qu'intervient le _filtre par `_user`_.

## Filtre par `_user`

```python
def _entry_matches(entry):
    expected_user = expected_login or env.get_credentials("dashboard")["login"]
    is_testing_entry = entry["_user"] == expected_user
    if not is_testing_entry:
        return False
    created_at = datetime.fromisoformat(entry["createdAtTimestampLackingMsPrecision"])
    return created_at >= min_utc_date - timedelta(seconds=1)
```

## ms amputées

```typescript
const createdAtTimestampLackingMsPrecision = new Date(
  now - (now % 1000),
).toISOString();
```

`createdAt` est arrondi _à la seconde_.  
Tous les `createdAt` d'OTP générés dans la même seconde sont _identiques_.  
Impossible de faire un tri ASC sur ces timestamps.

## Cycle et coordination

```
Worker A : min_utc_date_A = 13:27:53.500
          OTP émis : createdAt = 13:27:53.000 (amputé)

Filtre : 13:27:53.000 >= 13:27:53.500 - 1s = 13:27:52.500   ✅ passe
```

Sans la marge `-1s`, on aurait raté l'OTP qu'on vient de demander.

Afin de créer une _fenêtre temporelle_ stable, le test force exceptionnellement un _sleep_ de 2.5s dans `start_to_login_with_otp` (facteur de 2.5 par rapport au _timedelta_).

```python
if workers > 1:
    with _get_lock():
        time.sleep(2.5)
        _send(username)
    else:
        _send(username)
```

Le système combine la recherche par `_user` au système de _delta timing_ et de verrous qui force l'exécution séquentielle avec fenêtre temporelle (_pause_/_interruption_, aussi appelé _suspension temporaire_) pour identifier _son_ OTP.

Si l'implémentation côté Ocarina _trichait_ en se basant uniquement sur le _timestamp_, elle se planterait dès qu'on parallélise.

## Extrait du README de `tests-workers`

```
### Quirks

Returns ISO timestamps precise to seconds only (`.000Z`) to force proper concurrency handling in test frameworks.
```

C'est volontaire, documenté, et c'est un _beau cadeau_ du _backend_&nbsp;: un _bug_ subtil que la suite doit gérer correctement.

## Pourquoi Redis et pas juste un lock local

Trois workers d'Ocarina = trois threads, un process _WebDriver_ rattaché à chaque thread.  
Soit **un process principal avec N threads auxquels s'attachent un process piloté par Selenium pour chacun**.

On _pourrait_ utiliser `threading.Lock` ici.

Mais&nbsp;:

- Si on **scale horizontalement** (deux machines lancent `ocarina-example` simultanément, ou simpement deux _terminaux_ différents sur la même machine = deux _processes_ Ocarina), `threading.Lock` ne suffit plus&nbsp;: il faut un lock _distribué_.
- Redis offre `setnx`-based locks via `redis.lock()`.

## Conclusion

Le _design intentionnel_ de `tests-workers` est de **rendre la coordination des tests difficile mais possible**. C'est un _terrain d'entraînement_. Les vrais SUTs ont souvent ce genre d'imprécision (_rate limit_, _timestamp_ précis seulement à la seconde près, etc.).
