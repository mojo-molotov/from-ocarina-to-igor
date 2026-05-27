# Ch 05 — Igoristan

Chapter brief for LLM navigation. Source articles: `site/content.en/05-igoristan/`.

## Articles

| File | Description |
| --- | --- |
| `01-stack.md` | Stack: React 19 / Vike SSG / Vite 7 / Tailwind 4 / Valibot / wireit / pnpm. Hosted on GitHub Pages. |
| `02-routes.md` | The 10 routes, their role, and their deliberate dose of chaos (random errors, random loaders, fake auth). |
| `03-use-auth.md` | The fake `useAuth` hook, MFA OTP flow, `Math.random() < 0.9` non-determinism. **Contains ASCII diagram.** |
| `04-key-components.md` | Key UI components: `LoginForm`, `ChaoticForm`, `Dropzone`, `RandomLoader`, etc. **Contains ASCII diagram.** |
| `05-wireit.md` | `wireit` pipeline graph: `prebuild`, `build`, `dev`, `lint`, `typecheck`, `ci:format-check`. **Contains ASCII diagram.** |
| `06-husky-commitlint.md` | Husky + lint-staged + commitlint + commitizen pipeline. **Contains ASCII diagram.** |
| `07-ci-deploy.md` | CI/CD: `ci-pr.yml` (3 parallel jobs: lint, typecheck, format-check) + `deploy.yml` (push main → GitHub Pages). |

## Key concepts

- **Deliberate chaos**: Igoristan is not a stable demo app. Random errors, flaky loaders, `Math.random()` gates, and fake OTP MFA are features, not bugs — they force the test framework to be resilient.
- **Fake `useAuth`**: the auth flow is entirely client-side, using `otplib` to generate TOTP codes. No real backend auth. The OTP seed is known; `tests-workers` provides the current code via its `/api/otp` endpoint.
- **10 routes**: each route tests a different aspect of the framework — happy paths, randomness, file upload (sacred upload), Corsicamon API, etc.
- **wireit**: dependency-aware task runner (like Make but for JS), replacing npm scripts. The pipeline is documented in article 05 with a graph.
- **Stack**: SSG (static site generation) via Vike means pages are pre-rendered HTML, no Node.js server at runtime. Deployed to GitHub Pages.
- **SUT relationship**: `ocarina-example` tests Igoristan. The two repos are designed together but kept separate.

## Diagrams

- `03-use-auth.md` — fake useAuth + MFA OTP flow.
- `04-key-components.md` — key UI components layout.
- `05-wireit.md` — wireit pipeline graph.
- `06-husky-commitlint.md` — Husky + commitlint pipeline.

## Connections

- The test suite that targets Igoristan → Ch 07
- OTP coordination backend → Ch 06
- CI workflows for Igoristan → Ch 10

## Not covered here

The actual JS/TS implementation detail of each route's business logic — the primer describes routes structurally. Read the `igoristan` source for full implementation.
