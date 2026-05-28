---
title: "04.04 — Tests du typage statique (pytest-mypy-plugins)"
description: "Les tests du typage statique d'Ocarina via pytest-mypy-plugins : vérifier que ce qui devrait être une erreur mypy en est bien une."
weight: 4
date: 2026-05-20
series: ["tests-internes"]
series_order: 4
tags: ["typage"]
---

# 04.04&nbsp;—&nbsp;Tests du _typage statique_ (`pytest-mypy-plugins`)

> Cinq fichiers `*test_types.yml` qui testent _le comportement du checker_. C'est une dimension de tests **unique** à Ocarina dans son genre&nbsp;: on s'assure que ce qui _devrait_ être une erreur _mypy_ en est bien une.

## Listing

```
tests/
├── dsl/
│   ├── invariants/test_types.yml
│   └── testing_with_railway/test_types.yml
└── opinionated/
    ├── cli/test_types.yml
    ├── infra/test_types.yml
    └── plugins/reports/...   (snapshots — pas YAML)
```

## YAML

```yaml
- case: compatible_predicate_types
  description: Predicates should accept values of compatible types
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_email, is_positive

    validate(1234).assert_that(is_positive)
    validate("a@a.com").assert_that(is_email)
```

Sans `out:`&nbsp;→&nbsp;on attend que `mypy` passe **sans erreur** sur le code donné.

```yaml
- case: incompatible_predicate_types
  description: Predicates should reject values of incompatible types
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive

    validate("lol").assert_that(is_positive)
  out: |
    main:4: error: Argument 1 to "assert_that" of "ValidationStartBlock" has incompatible type "Callable[[float], None]"; expected "Callable[[str], None]"  [arg-type]
```

Avec `out:`&nbsp;→&nbsp;on attend ce message d'erreur _précis_ de _mypy_.

## Exemples de cas testés (invariants)

```yaml
- case: generics_preserved_through_chain
  description: Generic type parameter T should be preserved across validation chain
  regex: true
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive

    result = validate(42).assert_that(is_positive)
    reveal_type(result)
  out: |
    main:5: note: Revealed type is .*ValidationAssertBlock\[.*int.*\]

- case: then_allows_type_change
  description: .then() should allow switching to a different type in the validation chain
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive, is_email

    validate(42).assert_that(is_positive).then("email@test.com").assert_that(is_email)

- case: otherwise_with_same_type
  description: .otherwise() should accept predicates of the same type
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive, is_not_zero

    validate(5).assert_that(is_positive).otherwise(is_not_zero)

- case: multiple_otherwise_preserves_type
  description: Multiple .otherwise() calls should preserve the same type throughout
  main: |
    validate(5) \
        .assert_that(is_equal_to(10)) \
        .otherwise(is_equal_to(20)) \
        .otherwise(is_positive) \
        .otherwise(is_not_zero)

- case: execute_returns_result_type
  description: .execute() should return ValidationResult regardless of validated type
  ...
```

## Exemples de cas testés (testing_with_railway)

```yaml
- case: act_preserves_TPOM
  description: act(pom: TPOM, action) preserves TPOM through the chain
  regex: true
  main: |
    from selenium.webdriver.remote.webdriver import WebDriver
    from ocarina.dsl.testing_with_railway.constructors.create_act import create_act

    class HomePage:
        def click(self) -> "HomePage": return self
        def get_current_title(self) -> str: return ""
        def verify(self): return self

    pom = HomePage()
    result = create_act(pom, lambda p: p.click())
    reveal_type(result)
  out: |
    main: note: Revealed type is .*ActionStart\[HomePage\]

- case: drive_page_refuses_heterogenous_TPOMs
  description: drive_page enforces TPOM uniformity at the type level
  main: |
    ...  # mélange HomePage + DashboardPage dans le même drive_page
  out: |
    main: error: Expected type 'ActionSuccess\[HomePage\]'; got 'ActionSuccess\[DashboardPage\]'
```

## Pourquoi tester le typage

### 1. La sécurité du DSL **dépend** du typage

La machine à états `ActionStart → ActionFailure → ActionSuccess → ActionChain` est sécurisée _par le typage_. Si une régression dans le code du DSL casse cette propriété, il faut le voir. Un test runtime ne suffit pas&nbsp;: il faut un test sur le checker.

### 2. Les `reveal_type` documentent les inférences

Quand on lit `reveal_type(result)` dans un test YAML, on comprend précisément ce que _mypy_ infère. Ces tests **documentent** les inférences attendues.

### 3. Refactor-safety

Si un contributeur refactor `validate` et casse la conservation du `T`, le test type yml le détecte. Pas besoin de relire chaque scénario utilisateur pour s'apercevoir que le checker laisse passer des choses qu'il devrait refuser.

## Invocation par pytest

```
pytest tests/dsl/invariants/test_types.yml
```

Le plugin `pytest-mypy-plugins` charge le YAML, exécute chaque `case`&nbsp;:

1. Crée un fichier Python avec le contenu de `main`.
2. Lance _mypy_ dessus.
3. Compare la sortie au champ `out` (ou attend rien si `out` absent).
4. PASS/FAIL en conséquence.

## `regex: true`

Quand `regex: true` est dans le `case`, le `out:` est interprété comme une regex (pas une chaîne littérale). Permet d'attraper des messages comme&nbsp;:

```yaml
out: |
  main: note: Revealed type is .*ValidationAssertBlock\[.*int.*\]
```

Le `.*int.*` accepte les variations du formatage de _mypy_ (qui peut afficher `int`, `Literal[42]`, `builtins.int*`, etc. selon les versions).

## DSL testé dynamiquement et statiquement

Toute modification à `validate.py`, `assertions.py`, `validation_chain.py`, `action_chain.py`, `chain_actions.py`, `match_page.py`, `create_act.py` doit faire passer&nbsp;:

- Les tests scénarios pytest (~comportement).
- Les cram tests (CLI).
- **Les tests YAML mypy** (~typage).

C'est ce qui rend le DSL **stable**&nbsp;: on ne peut pas le casser, à _aucun_ niveau, sans qu'un test rouge ne le signale.

## L'absence côté `pyproject.toml`

```toml
[tool.coverage.run]
omit = [
    ...
    "src/ocarina/custom_types/*",
    "src/ocarina/ports/*",
    "src/ocarina/opinionated/cli/phantoms.py",
    ...
]
```

Ces fichiers _shape_ ne sont pas dans la couverture de pytest (la détection se passe sur du code exécuté dynamiquement, cet outil de coverage ne prend pas en compte les tests statiques).

La couverture est ici apportée **par les tests `pytest-mypy-plugins` (YAML).**
