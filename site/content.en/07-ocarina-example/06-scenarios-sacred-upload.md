---
title: "07.06 — Sacred upload scenarios"
description: "The sacred upload scenarios of ocarina-example: the file drag-and-drop that exercises Ocarina's upload pattern."
weight: 6
date: 2026-05-20
series: ["ocarina-example"]
series_order: 6
---

# 07.06&nbsp;—&nbsp;Sacred upload scenarios

> The `/igoristan/sacred-upload` page lets you drag-and-drop a file. Exercises the **file-upload** pattern on the Ocarina side.

## Campaign

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

## Scenario: upload files

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
        file_input.send_keys(str(file_path.resolve()))     # ← Selenium pattern: send_keys on input[type=file]
        return self

    def verify_file_uploaded(self, filename: str) -> SacredUploadPage:
        WebDriverWait(self._driver, get_timeout()).until(
            ec.text_to_be_present_in_element(self._uploaded_preview, filename)
        )
        return self
```

Standard Selenium pattern: `send_keys(<absolute path>)` on an `input[type=file]`, even if the input is hidden. Selenium bypasses browser security for file inputs only.

`react-dropzone` keeps a hidden `<input type="file">` behind the visible dropzone. Selenium finds it and `send_keys` does the rest.

## Fixtures

```
src/pages/sacred_upload/fixtures/
└── sample.png                                  # an exemplar file to upload
```

Fixtures are co-located with the POM, not the scenario. Not a convention&nbsp;—&nbsp;just a free choice.

## Parameterized connectors

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

Closure (see [`../03-functional/02-closures-ioc.md`](../03-functional/02-closures-ioc.md)).

## `unhappy_paths.py`

- **`try_to_upload_too_much_files_immediately`**: drop 900 files at once → no image recorded.
- **`try_to_upload_too_much_files_after_first_insertion`**: drop 1 file, then try 900 more → only the first file stays.

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
