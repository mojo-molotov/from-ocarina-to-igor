---
title: "05.02 — Igoristan routes"
description: "The Igoristan's ten routes, their role in the SUT and their dose of deliberate chaos to exercise Ocarina."
weight: 2
date: 2026-05-20
series: ["igoristan"]
series_order: 2
tags: ["watcher"]
---

# 05.02&nbsp;—&nbsp;Igoristan routes

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

| Route                     | URL                                        | Role                                             | Deliberate chaos                                           |
| ------------------------- | ------------------------------------------ | ------------------------------------------------ | ---------------------------------------------------------- |
| `HOME`                    | `/igoristan/`                              | Home with links to other pages, autoplay audio   | &nbsp;—&nbsp;                                              |
| `RANDOM_LOADERS`          | `/igoristan/random-loaders`                | Pseudo-random loaders                            | Loaders that stay visible for a variable time              |
| `SACRED_UPLOAD`           | `/igoristan/sacred-upload`                 | `react-dropzone` upload form                     | &nbsp;—&nbsp;                                              |
| `DASHBOARD`               | `/igoristan/dashboard`                     | Login (password `figatellu`), optional MFA OTP   | `useAuth` may fail 10% of the time even with the right pwd |
| `DASHBOARD_NESTED`        | `/igoristan/dashboard/nested`              | Protected page, requires MFA                     | &nbsp;—&nbsp;                                              |
| `CORSICAMON`              | `/igoristan/corsicamon`                    | "_Corsican Pokédex_", 3 random picks via API key | 1/5 chance of artificially raising `Error('lol')`          |
| `RANDOM_ERROR`            | `/igoristan/random-error`                  | Fake error page                                  | Title matched by `ERROR_PAGE_REGEX` on the test side       |
| `CHAOTIC_FORM`            | `/igoristan/chaotic-form`                  | Unstable form                                    | `.catch-me-if-you-can` elements appear at random           |
| `MADNESS`                 | `/igoristan/madness`                       | Alternating stories (Cors, ThisIsBastia)         | Renders one OR the other at random                         |
| `DONKEY_SAUSAGE_DETECTOR` | `/igoristan/donkey-sausage-eater-detector` | Detector for filthy Sicilian shits               | 30% random fail (BSOD-style)                               |

## Page by page

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

8 links to the other pages + autoplay audio Angelus of Jerusalem (amen 🙏).

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

`<ChaoticForm />` includes `.catch-me-if-you-can` elements that pop in and out at random&nbsp;—&nbsp;the exact use case for `Watcher` on the Ocarina side (see [`../02-ocarina/07-watcher.md`](../02-ocarina/07-watcher.md), [`../07-ocarina-example/09-watcher-catch-me.md`](../07-ocarina-example/09-watcher-catch-me.md)).

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
        throw new Error('lol');                        // ◄── 1/5 chance of artificial failure
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

1. **Random pick** of 3 distinct IDs between 1 and 8.
2. **Artificial failure** 1 in 5 ("_lol_").
3. **Parallel fetch** of the 3 entries via `Promise.all`.

On the tests side:

- `corsicamon_enter_api_key.py`: enters the API key into the UI.
- `corsicamon_main.py`: draw, error handling ("_lol_"), retries.

### `donkey-sausage-eater-detector`

```tsx
const DonkeySausageEaterDetector = () => {
  const [state, setState] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    const hasError = Math.random() < 0.3;                    // ◄── 30% fail
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

Random delay (700–2200 ms), dynamic title (with/without `500`), alternating components (`ApprovedVisitorWelcomePage` vs `DisapprovedVisitorGetOutPage`).

On the Ocarina side, this triggers:

- The `on_failure` hook on `act` that detects `ERROR_PAGE_REGEX` (see [`../07-ocarina-example/02-adapters.md`](../07-ocarina-example/02-adapters.md)).
- The transformation into `HttpErrorPageReachedError` → caught by `transient_errors` → retry.
- OR use of `match_page` (when defined in a scenario).

### dashboard

Special case: see [`03-use-auth.md`](03-use-auth.md) for `useAuth` and OTP details.

### Other pages

- **`random-loaders`**: loaders that take more or less time to display a result.
- **`random-error`**: deliberate error page with `ErrorCode`, `InternalErrorMsg` components.
- **`madness`**: `Cors` and `ThisIsBastia` rendered alternately.
- **`sacred-upload`**: Dropzone + preview, log files uploads.

## The sitemap excludes `/dashboard/**`

```ts
// vite.config.ts
const SITEMAP_EXCLUSIONS = ['**/igoristan/dashboard/**'] as const;
...
sitemap({
  sitemapGenerator: (entries) => entries.filter((e) => !minimatch(new URL(e.loc).pathname, SITEMAP_EXCLUSIONS[0])),
  ...
})
```

→ The authenticated page stays out of the sitemap. Standard SEO convention for protected pages.
