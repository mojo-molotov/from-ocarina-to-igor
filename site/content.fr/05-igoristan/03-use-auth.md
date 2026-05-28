---
title: "05.03 — Le faux useAuth + MFA OTP"
description: "Le faux hook useAuth de l'Igoristan : un échec aléatoire de 10% et un MFA OTP optionnel, pour exercer le rejeu et la coordination des workers."
weight: 3
date: 2026-05-20
series: ["igoristan"]
series_order: 3
tags: ["otp"]
---

# 05.03&nbsp;—&nbsp;Le faux `useAuth` + MFA OTP

> Le hook `useAuth` de l'Igoristan est volontairement faux. Il introduit deux mécaniques pour exercer le rejeu et la coordination des workers d'Ocarina&nbsp;: un échec aléatoire de 10% et un MFA OTP optionnel.

## Code

```ts
// src/hooks/useAuth.ts
const VALID_PASSWORD = "figatellu";
const NOT_AUTHENTICATED = -1;
const AUTHENTICATED_WITHOUT_MFA = 1;
const AUTHENTICATED_WITH_MFA = 2;

// * ... This is FAKED
export const useAuth = () => {
  const [_isAuthenticated, setIsAuthenticated] = useLocalStorage(
    "isAuthenticated",
    NOT_AUTHENTICATED,
  );
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = useCallback(
    () => _isAuthenticated !== NOT_AUTHENTICATED,
    [_isAuthenticated],
  );
  const isAuthenticatedWithMFA = useCallback(
    () => _isAuthenticated === AUTHENTICATED_WITH_MFA,
    [_isAuthenticated],
  );
  const logout = useCallback(
    () => setIsAuthenticated(NOT_AUTHENTICATED),
    [setIsAuthenticated],
  );

  useEffect(() => {
    const delay = 500 * randint(1, 5); // ◄── délai aléatoire 0.5-2.5s
    const timer = setTimeout(() => setIsLoading(false), delay);
    return () => clearTimeout(timer);
  }, []);

  const login: LoginFn = ({ pre = false, password, withMFA }) => {
    if (password === VALID_PASSWORD && Math.random() < 0.9) {
      // ◄── 10% d'échec malgré bon mdp
      if (!pre) {
        setIsAuthenticated(
          withMFA ? AUTHENTICATED_WITH_MFA : AUTHENTICATED_WITHOUT_MFA,
        );
      }
      return true;
    }
    return false;
  };

  return { isAuthenticatedWithMFA, isAuthenticated, isLoading, logout, login };
};
```

## Mécaniques

### 1. `LocalStorage`

```ts
const [_isAuthenticated, setIsAuthenticated] = useLocalStorage(
  "isAuthenticated",
  NOT_AUTHENTICATED,
);
```

Trois valeurs&nbsp;: `-1` (pas authentifié), `1` (sans MFA), `2` (avec MFA).  
Persistées dans `localStorage`, faciles d'accès pour du test/debug manuel.

### 2. Le mot de passe est en clair

```ts
const VALID_PASSWORD = "figatellu";
```

Public, hardcodé&nbsp;: on est sur une démo.

### 3. **Échec aléatoire**

```ts
if (password === VALID_PASSWORD && Math.random() < 0.9) {
```

On accepte le login _seulement_ si le mot de passe est bon **ET** un random tiré < 0.9. Donc 10% de chance d'**échec malgré le bon mot de passe**.

C'est **le** point clé du SUT pour exercer le rejeu avec Ocarina&nbsp;:

| Côté projet                                   | Comportement                                                      |
| --------------------------------------------- | ----------------------------------------------------------------- |
| Test passe avec succès                        | OK (90% des cas)                                                  |
| Test échoue avec «&nbsp;_Login failed_&nbsp;» | Retry géré _directement dans le POM_ (pas via `transient_errors`) |
| Test échoue 9 fois de suite                   | Probabilité = `0.1^9 ≈ 10⁻⁹`&nbsp;→&nbsp; infaisable              |

→ Avec `max_retries_per_test=8` (default), un test login a une probabilité d'échec inférieure à `10⁻⁹`.  
Sans retry, ce serait 10%.

C'est la **démonstration empirique** de la valeur des retries.

### 4. Délai d'initialisation aléatoire

```ts
const delay = 500 * randint(1, 5); // 500, 1000, 1500, 2000, 2500
const timer = setTimeout(() => setIsLoading(false), delay);
```

→ `isLoading = true` pendant 0.5 à 2.5 secondes au démarrage. Côté tests, on doit attendre que `isLoading` passe à `false` avant d'interagir, confirme l'utilité de `WebDriverWait` et détecte les races conditions liées à une utilisation trop agressive de `.find_element` avec Selenium.

### 5. Le `pre` mode dans `login`

```ts
const login: LoginFn = ({ pre = false, password, withMFA }) => {
    if (password === VALID_PASSWORD && Math.random() < 0.9) {
      if (!pre) {
        setIsAuthenticated(...);
      }
      return true;
    }
    return false;
};
```

Le `pre = true` permet de **valider le mot de passe sans authentifier**, utile pour le UI flow MFA&nbsp;: on valide le mot de passe, on _enchaîne_ vers l'écran OTP, et on n'authentifie qu'après que l'OTP est aussi validé.

## Flux (MFA)

```
1. UTILISATEUR / SELENIUM tape username + password + coche "Use OTP"
   ↓
2. login({ pre: true, password, withMFA: true })
   ↓
3. Si OK → fetch /api/otp?_user=<username> (vers tests-workers)
   ↓
4. tests-workers : redis.set otp:<ts>:<uuid> = { otpCode, ... }
   ↓
5. UI affiche écran OTP
   ↓
6. UTILISATEUR / SELENIUM tape le code OTP
   ↓
7. login({ pre: false, password, withMFA: true }) → setIsAuthenticated(2)
```

## Récupération d'OTP côté Ocarina

```python
# ocarina-example/src/api/retrieve_dashboard_otp_code.py
def retrieve_dashboard_otp_code(*, min_utc_date, timeout, expected_login=None):
    env = create_env_getters()
    igor_api_key = env.get_value("igor_api_key")
    entries = get_otp_history(igor_api_key=igor_api_key, timeout=timeout)

    def _entry_matches(entry):
        expected_user = expected_login or env.get_credentials("dashboard")["login"]
        is_testing_entry = entry["_user"] == expected_user
        if not is_testing_entry:
            return False
        created_at = datetime.fromisoformat(entry["createdAtTimestampLackingMsPrecision"])
        return created_at >= min_utc_date - timedelta(seconds=1)

    matching = list(filter(_entry_matches, entries))
    if not matching:
        return None
    matching.sort(key=lambda e: e["createdAtTimestampLackingMsPrecision"])
    return matching[0]["otpCode"]
```

1. Récupère **tout** l'historique OTP.
2. Filtre par `_user`.
3. Filtre par `createdAt >= min_utc_date - 1s` (marge pour _clock skew_).
4. Trie par date ascendante.
5. Retourne le **premier match** (le plus ancien).

C'est le _premier_ qui est probablement encore dans la fenêtre de validité (le TTL d'un OTP est de 5 min côté `tests-workers`).

## Coordination via Redis (`OTP_SEND_LOCK_KEY`)

Pour éviter que deux workers cliquent _en même temps_ (à la même seconde) sur «&nbsp;_Send OTP_&nbsp;» pour le même user, `ocarina-example` utilise un **lock Redis distribué**&nbsp;:

```python
# pages/dashboard/login.py
def _get_lock() -> RedisLock:
    client = get_redis_client()
    redis_lock: RedisLock = client.lock(OTP_SEND_LOCK_KEY, timeout=60)
    return redis_lock
```

Cf. [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md)

## Écran OTP, côté UI

```tsx
// src/components/LoginForm.tsx (extrait)
if (useOTP && !otpResponse) {
  const success = onLogin({ withMFA: true, pre: true, password });
  if (!success) {
    setError('Invalid credentials. Try any:figatellu');
    return;
  }
  ...
  const response = await fetch(`https://tests-workers.vercel.app/api/otp?_user=${encodeURIComponent(username)}`, {
    headers: { 'x-api-key': otpApiKey },
    signal: abortControllerRef.current.signal
  });
  ...
}
```

1. `login({ pre: true })`, pas encore authentifié, juste validation du mdp.
2. `fetch('/api/otp?_user=<u>', { headers: { 'x-api-key': <user-typed-key> } })`, récupère un OTP.
3. Affichage de l'écran OTP, attente du code.
