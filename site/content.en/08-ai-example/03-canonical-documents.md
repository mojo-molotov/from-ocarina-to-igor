---
title: "08.03 — Documentation"
description: "The AI project is the most documented in the Ocarina ecosystem."
weight: 3
date: 2026-05-20
series: ["ai-example"]
series_order: 3
---

# 08.03&nbsp;—&nbsp;Documentation

> The AI project is the most documented in the Ocarina ecosystem.

## Listing

| Document                | Status                            | Audience                  |
| ----------------------- | --------------------------------- | ------------------------- |
| `CLAUDE.md`             | Claude ↔ project working contract | Claude + any contributor  |
| `CURA_FRD.md`           | Reconstructed spec                | Maintainers, stakeholders |
| `CURA_TEST_STRATEGY.md` | Test strategy                     | Maintainers               |
| `IDENTIFIED_GAPS.md`    | Technical inventory of gaps       | Maintainers               |

## `CLAUDE.md`

1. **Key documents**: points to `README.md`, `CURA_FRD.md`, `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md`, `CLAUDE.local.md`.
2. **Project**: 2 sentences on the project (CURA, Python 3.14+, demo creds).
3. **Project philosophy**: "_No tricks or hacks. Teach the pattern, not the symptom._"
4. **`CLAUDE.local.md` template**: what the gitignored file should contain.
5. **Layout**: full `src/` tree, audited (shell command that verifies `CLAUDE.md` and the real tree stay in sync).
6. **Ocarina hierarchy**: reminder `Test → Suite → Campaign → Cycle`.
7. **Test strategy**: cycle structure, smoke gate, taxonomy.
8. **Running tests**: CLI commands.
9. **Reports and screenshots**: "one screenshot per drive_page" rule.
10. **Scenario fragments**: when to extract a fragment.
11. **Data-driven tests**: when to use the pattern, naming conventions.
12. **Shared mixins**: `SeleniumBackAndForwardNavigationMixin`.
13. **Conventions**: 12 concrete rules (TYPE_CHECKING guard, log factories, etc.).
14. **Hard-won rules**: rules drawn from experience, with past examples.

## Hard-won rules

### "_Verify SUT behaviour&nbsp;—&nbsp;don't theorise_"

> CURA is open source. Before building on a server-side claim, read the PHP:
>
> ```bash
> gh api repos/katalon-studio/katalon-demo-cura/contents/<file>.php --jq '.content' | base64 -d
> ```

No inference. Read the source, then assert.

### "_Inspect the SUT for security / spec gaps_"

> This is the **encouraged** use of source inspection.

Source reading is encouraged specifically to hunt for gaps.

### "_Security testing is functional and static&nbsp;—&nbsp;never active_"

> **Forbidden, no exceptions:**
>
> - Crafted attack payloads of any kind: SQL injection strings, XSS / HTML / JS payloads, command injection, header/parameter pollution, path traversal, deserialisation payloads.
> - Token tampering, signature stripping, cookie forgery, session-fixation attempts, forced-browsing fuzzers.
> - Cross-origin POSTs constructed outside the suite, scripted directory enumeration, DOS, rate-floods.

**Functional** security tests only ("use the app like a user"). Never active ("attack the app like an adversary").

### "_Throwaway probes&nbsp;—&nbsp;when source-reading and the suite don't agree_"

> A **probe** is a one-off script that drives the browser (or raw HTTP) through a suspect flow and prints concrete runtime state. It **bypasses the Ocarina workflow entirely**&nbsp;—&nbsp;no `create_selenium_test`, no suites, no campaigns, no assertions. Probes live in a gitignored directory, are **never committed or pushed**, and are deleted once the answer lands in a durable artifact.

Write throwaway scripts to explore. **Never commit them.** Findings land in an artifact (gap, FRD update, test).

### "A probe must exercise the _exact_ target the code under test will use"

> "Exact target" means **all** of: exact locator, exact screen / page state, exact wait condition, exact action.

A probe of something else proves nothing about what's being tested. Empiricism means you do and redo against the exact target.

### "_Probe sequences vs ritual workarounds&nbsp;—&nbsp;multi-action "dances"_"

> **Probe sequence (legitimate).** The dance _is_ the test.
> **Ritual workaround (not legitimate).** Glue around a _hypothesis_ about SUT behaviour.

A sequence of actions is either the test or a workaround. Remove a step and the test changes what it verifies → probe. Remove a step and it just breaks → workaround to eliminate.

### "_A cross-browser behavioural difference is a finding, not a test to route around_"

> **Never skip a test on the browser where it fails.**

Test fails on Chrome but passes on Firefox → **it's a finding**. Document it, keep it failing on Chrome. Don't skip.

### "_Functional testing simulates a real human&nbsp;—&nbsp;ask "would a real person hit this?"_"

> Every test here stands in for a person clicking through CURA in a browser.

An automated test simulates a human's journey. If the test fails but a real user would succeed under the same conditions → **the problem is in the test**. Otherwise → it's an anomaly.

### "_Confirming a back-forward-cache exposure&nbsp;—&nbsp;the back-then-reload check_"

Recipe to confirm a BFCache issue: `back()` then `refresh()`. If `back()` shows a protected page with no redirect, but `refresh()` does redirect → BFCache hit, confirmed anomaly.

### "_Scenario file structure_"

> **One scenario per file.** (...)
> **Top docstring gives the flow as arrows.** A reader must know exactly what the file exercises before reading any code.

Structural discipline: an arrow docstring (`open → fill → submit → verify`) at the top of every scenario file. One file per scenario.

### "_POM selectors live at the top of the class_"

All selectors grouped at the top of their respective POM. Don't scatter them.

### "Always use WebDriverWait&nbsp;—&nbsp;never raw find_element"

Precise table of which `expected_conditions` to use in each case. Never raw `find_element`.

### "_Widget-decorated inputs: drive the widget's API, don't fight its intercepts_"

For datepickers: bypass the component's UX wizardry, interact via JS, call its API. Cited example: `AppointmentPage.enter_visit_date` (Bootstrap 3 datepicker).

### "_Setup/teardown actions: prefer the URL, save the UI click for the test that owns it_"

Use the most direct path to set up a test (URL, API, injected session, fixtures). Only click the UI if the test genuinely verifies that UI interaction.

## `CURA_FRD.md`

1. Executive Summary
2. System Overview (purpose, stakeholders, deployment)
3. User Roles & Personas (authenticated, unauthenticated, demo)
4. **Functional Requirements** (Auth, Appointment, History, Profile)&nbsp;—&nbsp;this is the core
5. Element IDs (DOM selectors)
6. URL map
7. Business rules
8. Error handling
9. **Known bugs / gaps** (§9.1 to §9.11)

Documentation **reconstructed** by AI to make the co-built work verifiable.

## `CURA_TEST_STRATEGY.md`

1. Scope (functional e2e, out: perf/accessibility/email/etc.)
2. Test objectives
3. **Test types**: happy / unhappy / edge / **business attack** / exploratory / **permanent security regression**
4. Coverage tables (REQ-AUTH-N × test_X)
5. Suite/campaign tree
6. Expected pass/fail breakdown
7. **Categories of results** (cf. README: intentional gap, cross-browser, real regression, transient)
8. Run notes

## `IDENTIFIED_GAPS.md`

| ID          | Category    | Subject                                                                                                                                                     |
| ----------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G-SEC-1     | Security    | No CSRF token on forms                                                                                                                                      |
| G-SEC-2     | Security    | `_f::logout()` doesn't destroy the cookie                                                                                                                   |
| G-SEC-3     | Security    | Strict `===` but no rate-limit/lockout/captcha                                                                                                              |
| G-DATA-1    | Data        | No server-side validation of visit_date                                                                                                                     |
| G-DATA-2    | Data        | No uniqueness constraints on appointments, no conflict checks                                                                                               |
| G-SPEC-1    | Spec        | Booking history sorted by booking order, not by appointment date on the page                                                                                |
| G-SPEC-2    | Spec        | Profile page present but empty                                                                                                                              |
| G-SPEC-3    | Spec        | An unauthorized access attempt redirects to the homepage, not the login page                                                                                |
| B-BROWSER-1 | Browser     | BFCache anomaly: protected pages can reappear after logout via the back button                                                                              |
| A-ENV-1     | Environment | POST issue when stressing with several workers (3)                                                                                                          |
| A-ENV-2     | Environment | Test-environment issue: Chrome shows an undesired modal mid-test due to demo password fragility (resolved by disabling the feature in the test environment) |

- **Where**: file:line of the responsible PHP.
- **Symptom**: what we observe.
- **GitHub source vs deployment**: the eventual difference.
- **Bonus bug** (if any): variants / cascading bugs.
- **Impact**: exploitable consequences.
- **Test(s)**: names of the tests that materialize it.
- **SFD ref**: pointer to `§9.X`.

Standard forensic format. Everything is verifiable.
