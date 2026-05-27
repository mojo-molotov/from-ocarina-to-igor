---
title: "07.06 — Scénarios sacred upload"
description: "La page /igoristan/sacred-upload permet de glisser-déposer un fichier. Exerce le pattern d'upload de fichiers côté Ocarina."
weight: 6
date: 2026-05-20
series: ["ocarina-example"]
series_order: 6
---

# 07.06&nbsp;—&nbsp;Scénarios sacred upload

> La page `/igoristan/sacred-upload` permet de glisser-déposer un fichier. Exerce le pattern d'**upload de fichiers** côté Ocarina.

## Campagne

```python
# src/tests/campaigns/sacred_upload.py
def create_igoristan_sacred_upload_campaign(*, drivers_pool) -> TestCampaign:
    return TestCampaign(
        name="Sacred upload",
        suites=[
            create_sacred_upload_happy_paths_test_suite(drivers_pool=drivers_pool),
            create_sacred_upload_unhappy_paths_test_suite(drivers_pool=drivers_pool),
        ],
    )
```

## Scénario&nbsp;: upload files

```python
# tests/scenarios/sacred_upload/upload_files.py
def scenario_upload_files(driver, logger):
    page = SacredUploadPage(driver=driver)
    fixture_dir = Path(__file__).parent.parent.parent.parent / "pages" / "sacred_upload" / "fixtures"
    file_to_upload = fixture_dir / "sample.png"

    return [
        drive_page(
            act(page, open_sacred_upload_page)...,
            act(page, verify_sacred_upload_page)...,
            act(page, upload_file(file_to_upload))...,
            act(page, verify_file_uploaded(file_to_upload.name))...,
        ),
    ]


test_upload_files = create_selenium_test(
    name="Sacred upload - upload a file",
    test_scenario=lambda driver, logger: Scenario(test_chain=scenario_upload_files(driver, logger)),
)
```

## `<input type="file">`

```python
class SacredUploadPage(SeleniumTitleMixin, POMBase):
    _file_input = (By.CSS_SELECTOR, "input[type='file']")
    _uploaded_preview = (By.CSS_SELECTOR, ".upload-preview")

    def upload_file(self, file_path: Path) -> SacredUploadPage:
        file_input = self._driver.find_element(*self._file_input)
        file_input.send_keys(str(file_path.resolve()))     # ← Selenium pattern: send_keys sur input[type=file]
        return self

    def verify_file_uploaded(self, filename: str) -> SacredUploadPage:
        WebDriverWait(self._driver, get_timeout()).until(
            ec.text_to_be_present_in_element(self._uploaded_preview, filename)
        )
        return self
```

Le **pattern Selenium standard**&nbsp;: `send_keys(<path absolu>)` sur un `input[type=file]` _même si l'input est invisible_. Selenium contourne la sécurité du navigateur pour les inputs file uniquement.

Note&nbsp;: `react-dropzone` (côté UI Igoristan) maintient un `<input type="file">` _caché_ derrière la dropzone visible. Selenium peut la trouver et y appliquer `send_keys`.

## Fixtures

```
src/pages/sacred_upload/fixtures/
└── sample.png                                  # un fichier exemplaire à uploader
```

Les fixtures sont co-localisées avec le POM (sous `pages/sacred_upload/fixtures/`), pas avec le scénario.  
Ce n'est pas vraiment une convention, c'est un choix libre.

## Connectors paramétrés

```python
def upload_file(file_path: Path) -> Callable[[SacredUploadPage], SacredUploadPage]:
    def unwrapped(p: SacredUploadPage) -> SacredUploadPage:
        return p.upload_file(file_path)
    return unwrapped


def verify_file_uploaded(filename: str) -> Callable[[SacredUploadPage], SacredUploadPage]:
    def unwrapped(p: SacredUploadPage) -> SacredUploadPage:
        return p.verify_file_uploaded(filename)
    return unwrapped
```

Closure (cf. [`../03-functional/02-closures-ioc.md`](../03-functional/02-closures-ioc.md)).

## `unhappy_paths.py`

- **`try_to_upload_too_much_files_immediately`**&nbsp;: on drop trop de fichiers d'un coup (`add_images(images_amount=900, failing=True)`)&nbsp;→&nbsp;aucune image enregistrée.
- **`try_to_upload_too_much_files_after_first_insertion`**&nbsp;: on droppe 1 fichier, puis on tente d'en ajouter 900 de plus (`add_images(images_amount=900, failing=True, forced_expected_img_amount=1)`)&nbsp;→&nbsp;seul le fichier du premier drop reste enregistré.

## `just_go_back_to_igoristan`

```python
# tests/scenarios/sacred_upload/just_go_back_to_igoristan.py
def scenario_back_to_igoristan(driver, logger):
    page = SacredUploadPage(driver=driver)
    return [
        drive_page(
            act(page, open_sacred_upload_page)...,
            act(page, click_back_to_igoristan)...,
        ),
    ]


test_back_to_igoristan = create_selenium_test(
    name="Sacred upload - Back to Igoristan",
    test_scenario=lambda driver, logger: Scenario(test_chain=scenario_back_to_igoristan(driver, logger)),
    post_test_scenarios_fragments=[verify_homepage],
)
```
