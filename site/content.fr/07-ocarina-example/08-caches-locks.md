---
title: "07.08 — Cache L1 + clés réservées + locks Redis distribués"
description: "Mécanique de coordination interne : un cache in-memory pour partager des valeurs au sein d'un test, un lock Redis pour sérialiser un click entre plusieurs workers."
weight: 8
date: 2026-05-20
series: ["ocarina-example"]
series_order: 8
---

# 07.08&nbsp;—&nbsp;Cache L1 + clés réservées + locks Redis distribués

> Mécanique de coordination interne&nbsp;: un cache in-memory pour partager des valeurs _au sein d'un test_, un lock Redis pour sérialiser un click _entre plusieurs workers_.

## Cache L1

```python
# src/caches/l1.py
from dogpile.cache import make_region

in_memory_cache_with_30m_ttl = make_region().configure(
    "dogpile.cache.memory", expiration_time=30 * 60
)
```

Un seul cache, global, `dogpile.cache.memory` backend, TTL 30 minutes.

Choix «&nbsp;_memory_&nbsp;»&nbsp;→&nbsp;tout vit en RAM, pas de Redis pour ce cache _local_.

## Pourquoi un cache L1&nbsp;?

Le DSL Ocarina est **statique**&nbsp;: un scénario _décrit_ une suite d'`act`.  
Mais parfois on a besoin de **partager une valeur** entre deux acts&nbsp;:

1. Le premier act clique sur «&nbsp;_Send OTP_&nbsp;»&nbsp;→&nbsp;on note la date.
2. Le second act récupère l'OTP en passant cette date à `retrieve_dashboard_otp_code(min_utc_date=...)`

## `reserve_free_cache_key`

```python
# src/caches/reserve_free_cache_key.py
import uuid
from threading import Lock
from dogpile.cache.api import NO_VALUE

_RESERVED_VALUE: Final[str] = "__RESERVED__"
_lock = Lock()


def reserve_free_cache_key(region: CacheRegion) -> str:
    while True:
        key_candidate = str(uuid.uuid4())
        with _lock:
            if region.get(key_candidate) == NO_VALUE:
                region.set(key_candidate, _RESERVED_VALUE)
                return key_candidate
```

1. Génère un UUID (candidat).
2. Acquiert le lock _local_ (`threading.Lock`).
3. Si la clé est libre dans le cache (`NO_VALUE` = pas dans le cache)&nbsp;:
   - Marque la clé `"__RESERVED__"` (pour empêcher qu'un autre thread la prenne).
   - Retourne la clé.
4. Sinon&nbsp;: boucle.

Le `Lock` empêche une race condition entre `get` et `set`.

## Exemple

```python
cache = in_memory_cache_with_30m_ttl
fresh_cache_key_for_username = reserve_free_cache_key(cache)
fresh_cache_key_for_otp_send_button_click_date = reserve_free_cache_key(cache)

return [
    drive_page(
        act(on_dashboard_login_page,
            start_to_login_with_otp_and_with_retries(
                dashboard_creds, retries_amount,
                cache=cache, logger=logger,
                username_cache_key=fresh_cache_key_for_username,
                otp_send_button_click_date_cache_key=fresh_cache_key_for_otp_send_button_click_date,
            ))...,
        act(on_dashboard_login_page,
            type_otp_with_retries(
                retries_amount,
                cache=cache, logger=logger,
                username_cache_key=fresh_cache_key_for_username,
                otp_send_button_click_date_cache_key=fresh_cache_key_for_otp_send_button_click_date,
            ))...,
    ),
]
```

Deux clés réservées (`username` et `otp_send_date`).  
Passées aux deux connectors.

Le premier connector **écrit** dans le cache (la date où on a cliqué sur «&nbsp;_Send_&nbsp;»).  
Le second **lit** (pour retrouver l'OTP correspondant via `retrieve_dashboard_otp_code(min_utc_date=...)`).

## Pourquoi des UUIDs et pas des noms statiques

```python
fresh_cache_key_for_username = reserve_free_cache_key(cache)
# = "f3a7b2c4-12d4-4abc-..."
```

Si on utilisait `"username"` directement, deux tests parallélisés _qui partagent le cache_ écraseraient mutuellement leur `username`.  
UUID = unicité garantie.

Le cache est `dogpile.cache.memory`&nbsp;→&nbsp;_shared_ entre les threads d'un même process.  
Donc les tests parallélisés _partagent_ le même cache. Une unicité stricte est obligatoire (_idempotency key_).

## Verrou distribué (Redis)

Pour la coordination _entre process_ (plusieurs terminaux ouverts) ou _entre machines_ (scaling horizontal)&nbsp;:

```python
# src/lib/ext/redis/client.py
from threading import Lock
import redis as _redis

_init_lock = Lock()
_redis_client: _redis.StrictRedis | None = None


def get_redis_client() -> _redis.StrictRedis:
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    with _init_lock:
        if _redis_client is not None:
            return _redis_client
        redis_url = create_env_getters().get_value("redis_url")
        client = _redis.StrictRedis.from_url(redis_url)
        client.ping()
        _redis_client = client

    return _redis_client


def warmup_redis_client() -> None:
    get_redis_client()
```

## `DashboardLoginPage`

```python
# pages/dashboard/login.py
from constants.sys.redis_keys import OTP_SEND_LOCK_KEY

def _get_lock() -> RedisLock:
    client = get_redis_client()
    redis_lock: RedisLock = client.lock(OTP_SEND_LOCK_KEY, timeout=60)
    return redis_lock


class DashboardLoginPage(...):
    def start_to_login_with_otp(self, creds, *, cache, ...):
        lock = _get_lock()
        with lock:                                # ← sérialise tous les clicks "Send OTP"
            self._click_send_otp()
            now = datetime.now(UTC)
            cache.set(otp_send_button_click_date_cache_key, now.isoformat())
            cache.set(username_cache_key, creds["login"])
        return self
```

Le `with lock` est un _context manager_.

1. À l'entrée&nbsp;: `SETNX` Redis avec timeout (60s, pour ne pas introduire de _deadlock_ distribué en cas de crash).
2. Si déjà locked&nbsp;: attente.
3. À la sortie&nbsp;: `DEL` Redis.

Sur N machines lancées en parallèle, seul un worker à la fois peut cliquer sur «&nbsp;_Send OTP_&nbsp;» pour _cette action_.

## `OTP_SEND_LOCK_KEY`

```python
# src/constants/sys/redis_keys.py
OTP_SEND_LOCK_KEY = "ocarina_example:otp_send_lock"
```

Convention de nommage&nbsp;: `<projet>:<purpose>`.

## `warmup_redis_client`

```python
# src/main.py
logger.info("Warming up the Redis client...")
warmup_redis_client()
logger.success("Redis client initialized!")
```

→ Force la création du client _avant_ que les tests démarrent.  
Si Redis est dead, on s'en rend compte tout de suite, pas au milieu d'un test.

## Récap.

| Mécanisme                                    | Type                          | Portée                                                  | Usage                                                                                                |
| -------------------------------------------- | ----------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `in_memory_cache_with_30m_ttl`               | `dogpile.cache.memory`        | Process (impacte tous les workers d'un process Ocarina) | Partager des valeurs tirées du contexte d'exécution de test entre les pas de test d'un même scénario |
| `reserve_free_cache_key`                     | UUID + `threading.Lock`       | Thread-safe                                             | Réserver une clé _unique_ dans le cache                                                              |
| `get_redis_client`                           | `redis.StrictRedis` Singleton | Process                                                 | Accéder au Redis                                                                                     |
| `client.lock(OTP_SEND_LOCK_KEY, timeout=60)` | Redis `SETNX`                 | Multi-process /&nbsp;multi-machines                     | Forcer les tests à attendre leur tour                                                                |

## Rappel du Holy Book

Chapitre _premiers jutsus_, section «&nbsp;_Programmation réactive&nbsp;:&nbsp;NON_&nbsp;»

> Les scénarios de test d'Ocarina sont volontairement statiques. Pourtant, une application web est dynamique et parfois, enregistrer une valeur à la volée pour la passer à une étape suivante est tout à fait légitime.
>
> Ocarina n'y répond pas. Il n'en a pas besoin.
>
> ### Réponse architecturale
>
> Ce qu'on cherche ici est un _cache in-memory_.
>
> On génère des clés juste avant le lancement de la chaîne de test, et on les passe aux actions du POM. Les actions enregistrent et consomment via une clé unique. Le scénario se contente de les fournir.

Et&nbsp;:

> **Verrous**&nbsp;: `threading.Lock` si un seul process à la fois, sinon verrous distribués Redis (`redis.StrictRedis` + `redis.lock`).

Convention claire&nbsp;: _in-memory_ pour _mono-process_ (comprendre&nbsp;: 1 process Ocarina), Redis pour _multi-process_ (comprendre&nbsp;: 2+ processes Ocarina avec _impact qui dépasse le contexte d'exécution local des tests_).
