---
title: "04.05 — Snapshot testing (syrupy)"
description: "syrupy est un plugin pytest qui sérialise la sortie d'un test dans un fichier .ambr et compare aux runs suivants. Utilisé pour la sortie de pretty_print_results et results_to_json."
weight: 5
date: 2026-05-20
series: ["tests-internes"]
series_order: 5
---

# 04.05&nbsp;—&nbsp;Snapshot testing (`syrupy`)

> `syrupy` est un plugin pytest qui sérialise la sortie d'un test dans un fichier `.ambr` et compare aux runs suivants. Utilisé pour la sortie de `pretty_print_results` et `results_to_json`.

## `.ambr`

```
tests/opinionated/plugins/reports/__snapshots__/
├── test_pretty_print_results.ambr
└── test_results_to_json.ambr
```

Généré et géré par `syrupy`.

## Exemple

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

Le `snapshot` (fixture de `syrupy`)&nbsp;:

- Premier run&nbsp;→&nbsp;écrit le contenu dans `.ambr`
- Runs suivants&nbsp;→&nbsp;compare. Si diff, le test fail.
- `pytest --snapshot-update` (ou `make update-snapshots`)&nbsp;→&nbsp;réécrit les snapshots avec la nouvelle valeur.

## Pourquoi pas direct un `assert out == "Dashboard\n• ..."`

| `assert out == "..."` direct                    | Snapshot                                        |
| ----------------------------------------------- | ----------------------------------------------- |
| Le test doit contenir _toute_ la sortie inline  | La sortie vit dans un fichier dédié             |
| Refactor de la sortie = rewrite le test         | Refactor de la sortie = `make update-snapshots` |
| Mauvaise lisibilité (\n, indentation difficile) | Lisible (le `.ambr` est human-readable)         |
| Pas de diff lisible en cas de fail              | `syrupy` produit un diff précis                 |

## `make update-snapshots`

```makefile
.PHONY: update-snapshots
update-snapshots:
	@echo "Running tests (only to update snapshots)..."
	-pytest --snapshot-update
```

Quand on change délibérément le format de `pretty_print_results` (par exemple «&nbsp;_passer de `›` à `››`_&nbsp;»), on lance `make update-snapshots` et on reviewe la diff git du `.ambr` pour valider le changement.

## `-` devant `pytest`

Le `-` est une convention Makefile&nbsp;: «&nbsp;_continue même si la commande fail_&nbsp;». `--snapshot-update` ne doit pas faire crasher Make si un test fail _avant_ d'écrire son snapshot. On veut juste écrire tous les snapshots qu'on peut.

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

→ On vérifie la **structure** JSON désérialisée.

## L'avantage majeur du snapshot pour les rapports

Le format de sortie d'un rapport est un **contrat**&nbsp;: un parseur en aval peut le lire. Le snapshot capture le contrat _exact_&nbsp;: si quelqu'un change la sortie par mégarde, le test fail.

C'est plus solide que d'écrire `assert "PASSED" in out and "FAILED" in out` (qui passerait silencieusement à une refonte complète du format).

## Tests qui _ne sont pas_ des snapshots

Tout ce qui n'est pas de la sortie formatée&nbsp;: on garde des assertions normales.

Le snapshot est réservé à&nbsp;:

- `pretty_print_results` (sortie ANSI hiérarchique).
- `results_to_json` (JSON structuré).

Le DOCX n'est pas snapshot-é (trop volumineux, format binaire), mais `test_docx_tests_proofs.py` vérifie qu'**un fichier valide est produit** et qu'**il contient certaines strings clés**.
