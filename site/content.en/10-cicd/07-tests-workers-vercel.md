---
title: "10.07 — tests-workers: no GitHub CI, auto Vercel deploy"
description: "The only repo in the ecosystem with no GitHub Actions workflow. Everything goes through Vercel."
weight: 7
date: 2026-05-20
series: ["ci-cd"]
series_order: 7
---

# 10.07&nbsp;—&nbsp;`tests-workers`: no GitHub CI, auto Vercel deploy

> The only repo in the ecosystem **without a GitHub Actions workflow**. Everything goes through Vercel.

## Content of `.github/`

```
tests-workers/
└── (no .github/ — no workflows)
```

No `ci.yml`. No `deploy.yml`. No GitHub action.

## `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "echo 'No build required'",
  "outputDirectory": ".",
  "framework": null
}
```

Vercel _detects_ the project as _TypeScript Edge Functions_, builds on the fly (transpiles TS at runtime).

## `package.json#scripts`

```json
{
  "scripts": {
    "vercel-build": "echo 'Build skipped'"
  }
}
```

`vercel-build` hook: `echo` no-op.  
Vercel doesn't try to build.

## Deployment (manual)

Documented in the README:

```bash
pnpm install
vercel env add API_SECRET
vercel env add UPSTASH_REDIS_REST_URL
vercel env add UPSTASH_REDIS_REST_TOKEN
vercel deploy
```

Four commands, run by the author from their machine.

## Why no GitHub CI

| Reason                                | Detail                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Vercel auto-deploys from the repo** | Vercel can be configured to deploy automatically on each GitHub push.                                                                                                                                                                                                                                                    |
| **No dynamic tests**                  | The code is not at risk, was tested manually, and won't be updated anymore. It's a finished project.                                                                                                                                                                                                                     |
| **No static checks**                  | No automated static tests either. Everything was tested manually. Issues on this component would quickly be detected via the e2e tests and are easily isolable and reproducible. Most of the time, in our experience, problems instead come from Upstash deciding to kill the Redis instance for no reason, for example. |

## Vercel auto-deploy

Vercel offers native GitHub integration:

- Connect the GitHub repo to a Vercel project.
- Vercel deploys each push to main → production.
- Vercel deploys each PR → preview URL.

The `vercel.json` and env vars are configured once on the Vercel dashboard. Nothing more to do afterwards.

## Production URL

```
https://tests-workers.vercel.app
```

With the endpoints:

```
https://tests-workers.vercel.app/api/otp?_user=<u>
https://tests-workers.vercel.app/api/otp-history
https://tests-workers.vercel.app/api/corsicadex?id=<n>
```

See [`../06-tests-workers/`](../06-tests-workers/)

## Contrast with the other deployments

| Repo                        | Hosting      | Deploy trigger               | CI YAML                          |
| --------------------------- | ------------ | ---------------------------- | -------------------------------- |
| `igoristan`                 | GitHub Pages | push main                    | `deploy.yml`                     |
| `ocarina-holy-book`         | GitHub Pages | push main                    | `deploy.yml`                     |
| `tests-workers`             | Vercel       | push main (auto Vercel)      | _none_                           |
| `ocarina` (Allure artifact) | GitHub Pages | push main + composite action | `main_ci.yml` + composite action |

Three different patterns. `tests-workers` is the only one to _fully delegate_ the deploy to a third-party service.

## Pros / cons

The project accepts vendor lock-in for simplicity. A project deployable in 30 seconds and trivially migratable if needed.

## The ISC license

`tests-workers` is under **ISC** (not MIT like the others). Comes from the Vercel CLI scaffold, which generates ISC by default. The author didn't even look.

Note: ISC ≈ MIT (both are permissive single-paragraph licenses). No practical difference for contributors.

## Security

`API_SECRET` is:

1. Stored in env vars on the Vercel side (dashboard).
2. Never committed to the repo.
3. Read at Worker _cold-start_ via `process.env.API_SECRET`.
