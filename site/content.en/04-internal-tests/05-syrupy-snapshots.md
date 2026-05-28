---
title: "04.05 — Snapshot testing (syrupy)"
description: "Ocarina's snapshot testing with syrupy: serializing the output of pretty_print_results and results_to_json, compared against later runs."
weight: 5
date: 2026-05-20
series: ["internal-tests"]
series_order: 5
---

# 04.05&nbsp;—&nbsp;Snapshot testing (`syrupy`)

> `syrupy` is a pytest plugin that serializes a test's output into a `.ambr` file and compares to subsequent runs. Used for the output of `pretty_print_results` and `results_to_json`.

## `.ambr`

```
tests/opinionated/plugins/reports/__snapshots__/
├── test_pretty_print_results.ambr
└── test_results_to_json.ambr
```

Generated and managed by `syrupy`.

## Example

```python
# tests/opinionated/plugins/reports/test_pretty_print_results.py
def test_pretty_print_results_renders_campaign_suite_test(snapshot, capsys):
    results = {
        "Dashboard": {
            "Login happy paths": {
                "Login - without OTP": (Ok(None), 5, "login_no_otp"),
                "Login - with OTP": (Fail(error=RuntimeError("OTP missed")), 8, "login_otp"),
                "Skipped one": (None, -1, "skipped_one"),
            },
        },
    }
    pretty_print_results(results, with_colors=False)
    out = capsys.readouterr().out
    assert out == snapshot
```

The `snapshot` (`syrupy` fixture):

- First run → writes the content to `.ambr`.
- Subsequent runs → compares. Diff → test fails.
- `pytest --snapshot-update` (or `make update-snapshots`) → rewrites the snapshots with the new value.

## Why not directly an `assert out == "Dashboard\n• ..."`

| Direct `assert out == "..."`                  | Snapshot                                  |
| --------------------------------------------- | ----------------------------------------- |
| The test must contain _all_ the output inline | The output lives in a dedicated file      |
| Output refactor = rewrite the test            | Output refactor = `make update-snapshots` |
| Poor readability (\n, hard indentation)       | Readable (the `.ambr` is human-readable)  |
| No readable diff on fail                      | `syrupy` produces a precise diff          |

## `make update-snapshots`

```makefile
.PHONY: update-snapshots
update-snapshots:
	@echo "Running tests (only to update snapshots)..."
	-pytest --snapshot-update
```

When you deliberately change `pretty_print_results`'s format (say "_switch from `›` to `››`_"), run `make update-snapshots` and review the `.ambr`'s git diff to validate the change.

## `-` before `pytest`

The `-` is a Makefile convention&nbsp;—&nbsp;"_keep going even if the command fails_". `--snapshot-update` shouldn't crash Make if a test fails _before_ writing its snapshot. We want every snapshot we can get.

## `test_results_to_json.py`

```python
def test_json_results_format(snapshot, tmp_path):
    results = {...}
    generate_json_results(results=results, output_dir=tmp_path, logger=MutedLogger())
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    content = json.loads(files[0].read_text())
    assert content == snapshot
```

→ We verify the deserialized JSON **structure**.

## The major snapshot advantage for reports

A report's output format is a **contract**: a downstream parser reads it. The snapshot captures the _exact_ contract&nbsp;—&nbsp;accidentally change the output and the test fails.

More solid than `assert "PASSED" in out and "FAILED" in out` (which would silently survive a complete format overhaul).

## Tests that _aren't_ snapshots

Anything that isn't formatted output stays on normal assertions.

Snapshot is reserved for:

- `pretty_print_results` (hierarchical ANSI output).
- `results_to_json` (structured JSON).

DOCX isn't snapshotted (too bulky, binary format), but `test_docx_tests_proofs.py` checks that **a valid file is produced** and **contains certain key strings**.
