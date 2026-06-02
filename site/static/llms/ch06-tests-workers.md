# Ch 06 — tests-workers

Chapter brief for LLM navigation. Source articles: `site/content.en/06-tests-workers/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. "Goals": ~7 TypeScript files total (3 endpoints, 2 `lib/`, 1 `consts/`) plus `package.json`/`vercel.json`, "deployable in 30 seconds" by a human. The only repo in the ecosystem under ISC (not MIT). |
| `01-stack-edge.md` | Stack: Vercel Edge Functions (`runtime: "edge"`), Upstash Redis, `otplib`. Three endpoints, two lib files, zero Next.js app code. |
| `02-otp-endpoint.md` | `GET /api/otp` — generates a TOTP code, stores event in Redis, returns free payload. |
| `03-otp-history.md` | `GET /api/otp-history` — Redis SCAN + returns every OTP event ever generated (for test assertions). |
| `04-corsicadex.md` | `GET /api/corsicadex?id=N` — static lookup returning Corsicadex entry by ID (no Redis, pure computation). |
| `05-is-authorized.md` | `isAuthorized.ts` — authorization check: `x-api-key` header or `apiKey` query param against env secret. |
| `06-redis-upstash.md` | `lib/redis.ts` — Upstash Redis client configuration (REST-based, edge-compatible). |
| `07-otp-coordination-flow.md` | Full OTP coordination flow diagram: Igoristan ↔ workers ↔ Ocarina test ↔ Redis. **Contains ASCII diagram.** |

## Key concepts

- **Three endpoints**: `/api/otp`, `/api/otp-history`, `/api/corsicadex`. That is the entire backend.
- **OTP purpose**: Igoristan's fake auth requires a TOTP code. Parallel test runs can't share a TOTP seed directly (race conditions). `tests-workers` provides a coordination point: each test calls `/api/otp` to get the current code, which is stored in Redis with a timestamp. `/api/otp-history` lets tests assert that the right code was used.
- **Corsicadex**: a static lookup table (Pokédex-style) for Corsica-themed entries used by one of Igoristan's routes. The endpoint is a pure lookup — no state.
- **Vercel Edge**: deployed to Vercel's edge network. The `runtime: "edge"` pragma means the functions run in V8 isolates, not Node.js. This constrains available APIs — hence Upstash (REST-based Redis, edge-compatible) instead of standard Redis clients.
- **Authorization**: every endpoint checks for a shared API key. Tests must supply it via header or query param.
- **No GitHub CI**: `tests-workers` has no GitHub Actions workflows. Deployment is handled automatically by Vercel on push to main. **Contains ASCII diagram** (article 07).
- **Deliberately tiny** (goals): ~7 TypeScript files total (3 endpoints, 2 `lib/`, 1 `consts/`) plus `package.json`/`vercel.json`, "deployable in 30 seconds" by a human (`pnpm install` → `vercel env add` → `vercel deploy`). It is the only repo in the ecosystem under **ISC** (not MIT), kept from the Vercel scaffold default.

## Diagrams

- `07-otp-coordination-flow.md` — OTP coordination flow (distributed tests).

## Connections

- The SUT that consumes OTP → Ch 05 (Igoristan, `03-use-auth.md`)
- The test suite that calls `tests-workers` → Ch 07 (`08-caches-locks.md`, OTP scenario)
- Vercel deploy flow → Ch 10 (`07-tests-workers-vercel.md`)

## Not covered here

Live Redis key state, current OTP values, Vercel environment variables. Real-time environment state is never documented in the primer.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
