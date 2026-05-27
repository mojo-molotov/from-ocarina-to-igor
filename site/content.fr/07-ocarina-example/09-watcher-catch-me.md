---
title: "07.09 — catch_me_if_you_can"
description: "Détecte les éléments parasites qui pop sur la page pendant que le test tourne, et les trace."
weight: 9
date: 2026-05-20
series: ["ocarina-example"]
series_order: 9
tags: ["watcher"]
---

# 07.09&nbsp;—&nbsp;`catch_me_if_you_can`

> Détecte les éléments parasites qui pop sur la page _pendant_ que le test tourne, et les trace.

## Callback

```python
# src/lib/ext/selenium/watchers/catch_me_if_you_can_watcher.py
def catch_me_if_you_can_cb(watcher: SeleniumWatcher) -> None:
    elements = watcher.driver.execute_script(
        "return Array.from(document.querySelectorAll('.catch-me-if-you-can'));"
    )

    if not elements:
        return

    raw = watcher.driver.execute_script(
        """
        return arguments[0].map(el => ({
            tag:       el.tagName.toLowerCase(),
            text:      el.innerText.trim(),
            id:        el.id,
            cls:       el.className,
            name:      el.getAttribute('name') || '',
            testid:    el.getAttribute('data-testid') || '',
        }));
        """,
        elements,
    )

    for attrs in raw:
        fingerprint = ":".join(
            filter(
                None,
                [
                    attrs["tag"],
                    attrs["text"],
                    attrs["id"],
                    attrs["cls"],
                    attrs["name"],
                    attrs["testid"],
                ],
            )
        )

        if fingerprint in watcher.cache:
            continue

        watcher.cache.add(fingerprint)
        watcher.report(
            f"catch-me-if-you-can element detected: <{attrs['tag']}> {attrs['text']!r}",
            label="CATCH_ME_IF_YOU_CAN",
        )
```

## Mécaniques

### 1. Javascript pour bypass implicit wait

```python
elements = watcher.driver.execute_script(
    "return Array.from(document.querySelectorAll('.catch-me-if-you-can'));"
)
```

Pas de `find_elements(By.CSS_SELECTOR, ...)`.

> Passer directement par du _Javascript_ permet de contourner toute logique de _polling_ interne et de rendre l'exécution du _watcher_ la moins bloquante possible pour le test qui tourne sur le même _driver_.

(Holy Book, _handling-flakiness_.)

Si le watcher utilisait `find_elements(By.CSS_SELECTOR, ".catch-me-if-you-can")` et qu'il n'y avait pas d'élément, Selenium attendrait `--wait-timeout` secondes (typiquement 10s) avant de retourner `[]`. Sur un _poll_ toutes les 0.8s, ça bloquerait tout.

En Javascript `querySelectorAll` est **synchrone et instantané**&nbsp;: ça retourne `[]` (liste vide) immédiatement s'il n'y a rien.

### 2. Early return

```python
if not elements:
    return
```

S'il n'y a rien&nbsp;: on arrête immédiatement.  
Le _poll_ suivant se déclenchera après `poll_interval`.

### 3. Extraction d'attrs en JS (un seul round-trip)

```python
raw = watcher.driver.execute_script(
    """
    return arguments[0].map(el => ({
        tag: el.tagName.toLowerCase(),
        text: el.innerText.trim(),
        ...
    }));
    """,
    elements,
)
```

Plutôt que de faire 6 round-trips Selenium par élément (`element.tag_name`, `element.text`, `element.get_attribute("id")`, etc.), on fait **un seul** appel JS qui retourne un array de dicts.

Performance&nbsp;: 6 _round-trips_ à 50ms = 300ms&nbsp;; 1 _round-trip_ = 50ms.  
Différence sensible quand on poll toutes les 800ms.

### 4. Fingerprint

```python
fingerprint = ":".join(filter(None, [
    attrs["tag"], attrs["text"], attrs["id"], attrs["cls"], attrs["name"], attrs["testid"],
]))
```

→ Pour un élément `<div class="catch-me-if-you-can" id="x" data-testid="y">Hello</div>`, fingerprint = `"div:Hello:x:catch-me-if-you-can:..."`.

Le `filter(None, ...)` enlève les strings vides, sinon on aurait `"div:Hello:x::cls::y"` avec double `::`.

### 5. Déduplication

```python
if fingerprint in watcher.cache:
    continue

watcher.cache.add(fingerprint)
watcher.report(...)
```

Si on a déjà reporté cet élément (même fingerprint), on _skip_.  
Le `watcher.cache` est un `set[str]` qui vit pendant toute la durée du `watcher` (i.e. du test).

Un même élément qui reste affiché pendant 5 polls successifs n'est reporté **qu'une fois**.  
Pas de spam.

### 6. `watcher.report`

```python
watcher.report(
    f"catch-me-if-you-can element detected: <{attrs['tag']}> {attrs['text']!r}",
    label="CATCH_ME_IF_YOU_CAN",
)
```

`watcher.report`&nbsp;:

1. `logger.info(message)`&nbsp;: apparaît dans les logs du watcher.
2. `take_screenshot(driver, logger, label)`&nbsp;: prend une capture d'écran avec le label `CATCH_ME_IF_YOU_CAN`.

Cf. [`../02-ocarina/07-watcher.md`](../02-ocarina/07-watcher.md) pour la mécanique du watcher.

## Taxonomie

```python
watcher_taxonomy = (*taxonomy[:-1], f"{test_name} - {watcher.name}")
scoped_logger = self._create_logger().set_domain_taxonomy(watcher_taxonomy)
watcher.start(driver, scoped_logger, self._take_screenshot)
```

Donc, avec le `FileLogger`, on génère un fichier `.log` distinct au même niveau que celui du test&nbsp;:

```
.ocarina_logs/
└── e2e/
    └── Randomness/
        └── Randomness/
            ├── Send the chaotic form.log                              # log du test
            └── Send the chaotic form - catch-me-if-you-can.log        # log du watcher
```

→ Le plugin de générations de preuves de test au format DOCX crée les deux côte à côte.

## Côté scénario

```python
test_send_chaotic_form = create_selenium_test(
    name="Send the chaotic form",
    test_scenario=lambda driver, logger: Scenario(
        test_chain=_send_chaotic_form(HumanizedDriver(driver, ...), logger),
        watchers=[
            create_selenium_watcher(
                callback=catch_me_if_you_can_cb,
                name="catch-me-if-you-can",
                poll_interval=0.8,
            ),
        ],
    ),
)
```

## «&nbsp;_Les watchers n'apportent que des mauvaises nouvelles_&nbsp;»

`CLAUDE.md`&nbsp;:

> **Les signaux des watchers sont négatifs uniquement.** Un watcher qui émet «&nbsp;_login réussi_&nbsp;» casse le contrat.

C'est le cas ici&nbsp;: un élément `.catch-me-if-you-can` est une **friction** qu'on _ne voulait pas voir_.  
Un watcher ne doit jamais dire «&nbsp;_tout va bien_&nbsp;»&nbsp;: **soit il râle, soit il se TAIT** (_Silence is Golden_).

Si on voulait un signal positif («&nbsp;_le toast de succès est apparu_&nbsp;»), ce serait dans `test_chain` via un `act`, pas dans un _watcher_.
