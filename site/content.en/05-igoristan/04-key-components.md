---
title: "05.04 — Key UI components"
description: "The src/components/ files and their role in the playground."
weight: 4
date: 2026-05-20
series: ["igoristan"]
series_order: 4
---

# 05.04&nbsp;—&nbsp;Key UI components

> The `src/components/` files and their role in the playground.

## Listing

```
src/components/
├── BackToHome.tsx              # back-to-HOME button
├── BackToSicily.tsx            # variant
├── Button.tsx                  # Tailwind-styled button
├── ChaoticForm.tsx             # ⭐ form with .catch-me-if-you-can elements
├── Dropzone.tsx                # ⭐ react-dropzone wrapper for SACRED_UPLOAD
├── ErrorCode.tsx               # component showing an HTTP code (used by RANDOM_ERROR)
├── FakeUpload/                 # fake upload component (animation, no real POST)
├── InternalErrorMsg.tsx        # generic error message
├── Label.tsx                   # form label
├── Link.tsx                    # styled <a> wrapper
├── Loading.tsx                 # generic spinner
├── LoginForm.tsx               # ⭐ login form + MFA OTP
├── PlusButton.tsx              # + button (corsicamon: add to collection)
├── RandomBibleVerse.tsx        # random bible verse
├── RandomLoader.tsx            # ⭐ random loader
├── UploadPreview.tsx           # preview of an uploaded file
└── XButton.tsx                 # X close button
```

⭐ = key component for Ocarina scenarios.

## `LoginForm.tsx`

### Architecture

```tsx
const LoginForm: FunctionComponent<LoginFormProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [useOTP, setUseOTP] = useState(false);
  const [otpApiKey, setOtpApiKey] = useState('');
  const [otpResponse, setOtpResponse] = useState<OTPResponse | null>(null);
  const [otpInput, setOtpInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortControllerRef.current?.abort(), []);

  const handleSubmit = async (e: FormEvent) => {
    ...
  };
  ...
};
```

| Mode             | Behavior                                                                              |
| ---------------- | ------------------------------------------------------------------------------------- |
| Without OTP      | `onLogin({ withMFA: false, password })` → if OK, authenticated                        |
| With OTP, step 1 | `onLogin({ withMFA: true, pre: true, password })` → if OK, fetch `/api/otp?_user=<u>` |
| With OTP, step 2 | The user types the OTP, `onLogin({ withMFA: true, password })` → authenticated        |

### `abortControllerRef`

```tsx
const abortControllerRef = useRef<AbortController | null>(null);

useEffect(() => () => abortControllerRef.current?.abort(), []);

...
abortControllerRef.current?.abort();
abortControllerRef.current = new AbortController();

const response = await fetch(`...`, { signal: abortControllerRef.current.signal });
```

→ Cancels an in-flight request when the user clicks "_Send OTP_" twice, or when the component unmounts.

### Schema validation (OTP service response)

```tsx
import { OTPResponseSchema } from "@/schemas/OTPResponseSchema";

const parseResult = safeParse(OTPResponseSchema, data);
if (!parseResult.success) {
  setError("Invalid OTP response format");
  return;
}
setOtpResponse(parseResult.output);
```

## `ChaoticForm.tsx`

- **Parasite validation** (error message appears on correct input).
- **Ephemeral toasts** (appear, vanish).
- **Form randomly rejected on submit** (incomprehensible random error message).

Tests side:

1. **`HumanizedDriver`** in `ocarina-example`&nbsp;—&nbsp;slows down typing, simulates keystrokes / typos / corrections.
2. **`Watcher` `catch_me_if_you_can_cb`**&nbsp;—&nbsp;catches parasite elements in the background.

## `Dropzone.tsx`

```tsx
const onDrop = useCallback((acceptedFiles: File[]) => {
  setFiles((prev) => [...prev, ...acceptedFiles]);
}, []);

const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });
```

- Multi-file drag-and-drop.
- Per-file preview via `UploadPreview`.
- No real upload&nbsp;—&nbsp;fake (animation, no POST).

`tests/scenarios/sacred_upload/upload_files.py`:

- Open the page,
- Drag a fixture file,
- Verify the preview.

## `RandomLoader.tsx`

```tsx
const LOADERS = [SpinnerStyle1, SpinnerStyle2, SpinnerStyle3, ...] as const;

const RandomLoader = () => {
  const [Loader] = useState(() => pickRandom(LOADERS));
  return <Loader />;
};
```

→ Picks a random loader **at creation time**. Lives for the component's lifetime.

Tests side: the `RANDOM_LOADERS` page shows several `RandomLoader`s; the test just verifies that _something_ shows up. No specific loader expected.

## `Loading.tsx` vs `RandomLoader.tsx`

| `Loading`                                    | `RandomLoader`             |
| -------------------------------------------- | -------------------------- |
| Fixed spinner (doesn't change)               | Picked at random           |
| Used by `Dashboard` (waiting on `isLoading`) | Used by `RANDOM_LOADERS`   |
| Deterministic behavior                       | Non-deterministic behavior |

## `ErrorCode.tsx` + `InternalErrorMsg.tsx`

Visual error components. Typically display "_500 Internal Server Error_". The `RANDOM_ERROR` page uses them to _simulate_ an error page, and the title gets matched by `ERROR_PAGE_REGEX` on the tests side.

## `RandomBibleVerse.tsx`

Cosmetic component: displays a random verse. So that the _Spam God_ may watch over Igoristan.

## `BackToHome.tsx` / `BackToSicily.tsx`

Links back to home, or sending you to a Sicilian site to eject the invaders. ✈️

## `LoginForm`

`tests/scenarios/dashboard/access/happy_paths.py`:

- `open_dashboard_login_page`,
- `verify_dashboard_login_page`,
- `login_without_otp_and_with_retries` (90% success, up to 10 retries to beat the odds),
- `start_to_login_with_otp_and_with_retries`,
- `verify_otp_screen`,
- `type_otp_with_retries`,
- `verify_dashboard_welcome_page`,
- `click_on_go_to_nested_page_btn`,
- `verify_dashboard_protected_page`.

~9 acts, so at least 2 `drive_page`s, sometimes 3. The most _complete_ case in the canonical suite.
