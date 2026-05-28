---
title: "05.02 — Les routes de l'Igoristan"
description: "Les dix routes de l'Igoristan, leur rôle dans le SUT et leur dose de chaos volontaire pour exercer Ocarina."
weight: 2
date: 2026-05-20
series: ["igoristan"]
series_order: 2
tags: ["watcher"]
---

# 05.02&nbsp;—&nbsp;Les routes de l'Igoristan

## `src/config/routes.ts`

```ts
const __ROOT = "/igoristan/";
const DASHBOARD = "dashboard";

const __ROUTES = {
  DONKEY_SAUSAGE_DETECTOR: "donkey-sausage-eater-detector",
  DASHBOARD_NESTED: `${DASHBOARD}/nested`,
  RANDOM_LOADERS: "random-loaders",
  SACRED_UPLOAD: "sacred-upload",
  RANDOM_ERROR: "random-error",
  CHAOTIC_FORM: "chaotic-form",
  CORSICAMON: "corsicamon",
  MADNESS: "madness",
  DASHBOARD,
  HOME: "",
} as const satisfies Routes;

const ROUTES = createRoutes(__ROUTES, __ROOT);
```

| Route                     | URL                                        | Rôle                                                            | Chaos volontaire                                           |
| ------------------------- | ------------------------------------------ | --------------------------------------------------------------- | ---------------------------------------------------------- |
| `HOME`                    | `/igoristan/`                              | Page d'accueil avec liens vers les autres pages, autoplay audio | &nbsp;—&nbsp;                                              |
| `RANDOM_LOADERS`          | `/igoristan/random-loaders`                | Loaders pseudo-aléatoires                                       | Loaders qui restent affichés un temps variable             |
| `SACRED_UPLOAD`           | `/igoristan/sacred-upload`                 | Formulaire d'upload `react-dropzone`                            | &nbsp;—&nbsp;                                              |
| `DASHBOARD`               | `/igoristan/dashboard`                     | Login (mot de passe `figatellu`), MFA OTP optionnel             | `useAuth` peut échouer 10% du temps même avec le bon mdp   |
| `DASHBOARD_NESTED`        | `/igoristan/dashboard/nested`              | Page protégée, requiert MFA                                     | &nbsp;—&nbsp;                                              |
| `CORSICAMON`              | `/igoristan/corsicamon`                    | «&nbsp;_Pokédex corse_&nbsp;», 3 picks aléatoires via API key   | 1/5 chance de lever `Error('lol')` artificiellement        |
| `RANDOM_ERROR`            | `/igoristan/random-error`                  | Page d'erreur factice                                           | Titre matché par `ERROR_PAGE_REGEX` côté tests             |
| `CHAOTIC_FORM`            | `/igoristan/chaotic-form`                  | Formulaire instable                                             | Éléments `.catch-me-if-you-can` apparaissent aléatoirement |
| `MADNESS`                 | `/igoristan/madness`                       | Histoires alternées (Cors, ThisIsBastia)                        | Rend l'une OU l'autre au hasard                            |
| `DONKEY_SAUSAGE_DETECTOR` | `/igoristan/donkey-sausage-eater-detector` | Détecteur de sales siciliens de merde                           | 30% d'échec aléatoire (BSOD-style)                         |

## Page par page

```ts
const links = [
  { href: ROUTES.RANDOM_LOADERS, label: "Random loaders" },
  { href: ROUTES.SACRED_UPLOAD, label: "Sacred upload" },
  { href: ROUTES.DASHBOARD, label: "Dashboard" },
  { href: ROUTES.CORSICAMON, label: "Corsicamon" },
  { href: ROUTES.RANDOM_ERROR, label: "Random Error" },
  { href: ROUTES.CHAOTIC_FORM, label: "Chaotic form" },
  { href: ROUTES.MADNESS, label: "Madness" },
  { href: ROUTES.DONKEY_SAUSAGE_DETECTOR, label: "Donkey Sausage Detector" },
];
```

### home

8 liens vers les autres pages + autoplay audio Angelus de Jérusalem (amen 🙏).

### chaotic-form

```tsx
const ChaoticFormPage = () => (
  <Main>
    <div className="mx-auto max-w-2xl">
      <h1 ...>Sacred Corsican Registration</h1>
      <ChaoticForm />
      <p ...>"Blessed are the Corsicans, for they shall inherit the Mediterranean" - Napoleon 4:20</p>
      <BackToHome ... />
    </div>
  </Main>
);
```

`<ChaoticForm />` inclut des éléments `.catch-me-if-you-can` qui apparaissent /&nbsp;disparaissent au hasard, exact cas d'usage du `Watcher` côté Ocarina (cf. [`../02-ocarina/07-watcher.md`](../02-ocarina/07-watcher.md), [`../07-ocarina-example/09-watcher-catch-me.md`](../07-ocarina-example/09-watcher-catch-me.md)).

### corsicamon

```tsx
const CORSICADEX_API = 'https://tests-workers.vercel.app/api/corsicadex';

export default function PokemonPicker() {
  const [apiKey, setApiKey] = useState<string>('');
  ...

  const fetchRandomPokemons = useCallback(async () => {
    ...
    while (ids.length < 3) {
      const randomId = Math.floor(Math.random() * 8) + 1;
      if (!ids.includes(randomId)) ids.push(randomId);
    }

    try {
      if (randint(1, 5) === 1) {
        throw new Error('lol');                        // ◄── 1/5 chance d'échec artificiel
      }
      const promises = ids.map(async (id) => {
        const res = await fetch(`${CORSICADEX_API}?id=${id}`, {
          headers: { 'x-api-key': apiKey }
        });
        return res.json();
      });
      ...
    } catch (err) {
      setFetchError(true);
    }
  }, [apiKey]);
}
```

1. **Pick aléatoire** de 3 IDs distincts entre 1 et 8.
2. **Échec artificiel** 1/5 («&nbsp;_lol_&nbsp;»).
3. **Fetch parallèle** des 3 fiches via `Promise.all`.

Côté tests&nbsp;:

- `corsicamon_enter_api_key.py`&nbsp;: entre l'API key dans l'UI.
- `corsicamon_main.py`&nbsp;: draw, gestion des erreurs («&nbsp;_lol_&nbsp;»), retries.

### `donkey-sausage-eater-detector`

```tsx
const DonkeySausageEaterDetector = () => {
  const [state, setState] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    const hasError = Math.random() < 0.3;                    // ◄── 30% d'échec
    const timeoutId = setTimeout(() => {
      document.title = formatPageTitle({
        pageTitle: hasError ? ERROR_PAGE_TITLE : PAGE_TITLE,
        errorCode: hasError ? '500' : undefined
      });
      setState(hasError ? 'error' : 'success');
    }, randint(1, 5) * 250 + 450);
    return () => clearTimeout(timeoutId);
  }, []);
  ...
};
```

Délai aléatoire (700-2200 ms), titre dynamique (avec/sans `500`), composants alternés (`ApprovedVisitorWelcomePage` vs `DisapprovedVisitorGetOutPage`).

Côté Ocarina, ça déclenche&nbsp;:

- Le hook `on_failure` côté `act` qui détecte `ERROR_PAGE_REGEX` (cf. [`../07-ocarina-example/02-adapters.md`](../07-ocarina-example/02-adapters.md)).
- La transformation en `HttpErrorPageReachedError`&nbsp;→&nbsp;catched par `transient_errors`&nbsp;→&nbsp;retry.
- OU l'utilisation de `match_page` (lorsqu'elle est définie dans un scénario)

### dashboard

Cas particulier&nbsp;: voir [`03-use-auth.md`](03-use-auth.md) pour le détail du `useAuth` et de l'OTP.

### Autres pages

- **`random-loaders`**&nbsp;: loaders qui mettent plus ou moins de temps à afficher un résultat.
- **`random-error`**&nbsp;: page d'erreur volontaire avec composants `ErrorCode`, `InternalErrorMsg`.
- **`madness`**&nbsp;: `Cors` et `ThisIsBastia` rendus alternativement.
- **`sacred-upload`**&nbsp;: Dropzone + preview, log files uploads.

## Le sitemap exclut `/dashboard/**`

```ts
// vite.config.ts
const SITEMAP_EXCLUSIONS = ['**/igoristan/dashboard/**'] as const;
...
sitemap({
  sitemapGenerator: (entries) => entries.filter((e) => !minimatch(new URL(e.loc).pathname, SITEMAP_EXCLUSIONS[0])),
  ...
})
```

→ La page authentifiée n'apparaît pas dans le sitemap. Convention SEO standard pour les pages protégées.
