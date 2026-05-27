# Ch 99 — References

Chapter brief for LLM navigation. Source articles: `site/content.en/99-references/`.

## Articles

| File | Description |
| --- | --- |
| `01-glossary.md` | Full glossary: ROP, ISTQB, Ocarina-specific terms, functional programming concepts, security terminology. |
| `02-file-index.md` | Per-repo index of every source file cited in the primer, with the article(s) that cite it. |

## Key concepts

- **Glossary**: the authoritative definition of every term used in the primer. If a term appears without explanation in another chapter, this is the lookup point.
- **Key glossary entries**: `Result[T]`, `Ok[T]`, `Err`, `ActionChain`, `Thunk[T]`, `Effect`, `TestCycle`, `TestCampaign`, `TestSuite`, `Test`, `Scenario`, `Watcher`, `POMBase`, `DriversPool`, `ROP`, `ISTQB`, `SUT`, `Corsicadex`, `HumanizedDriver`, `EnvGetters`, `skill` (LLM procedure), `llms.txt`.
- **File index**: maps source files in each of the six repos to the primer articles that discuss them. Use this to find which primer article covers a specific file you're looking at in the source.
- **Cited people**: the glossary section on cited people gives brief identifications for every person named in the primer (Wlaschin, Church, Wadler, Moggi, DHH, Paul Graham, YTCracker, Yung Innanet, Roberto Preatoni, Terry Davis, etc.).

## Connections

- Every other chapter references this one implicitly. If a term is unfamiliar, come here first.
- File index cross-references: → Ch 02 (framework files), Ch 05 (Igoristan files), Ch 06 (tests-workers files), Ch 07 (ocarina-example files), Ch 08 (AI example files), Ch 09 (Holy Book files).

## Not covered here

API documentation (consult the framework source and docstrings). Installation / setup (consult the Holy Book). This chapter indexes what the primer covers — not what it doesn't cover.
