---
title: "05.04 — Composants UI clés"
description: "Les composants src/components/ et leur rôle dans le terrain de jeu."
weight: 4
date: 2026-05-20
series: ["igoristan"]
series_order: 4
---

# 05.04&nbsp;—&nbsp;Composants UI clés

> Les composants `src/components/` et leur rôle dans le terrain de jeu.

## Listing

```
src/components/
├── BackToHome.tsx              # bouton de retour à HOME
├── BackToSicily.tsx            # variante
├── Button.tsx                  # button stylisé Tailwind
├── ChaoticForm.tsx             # ⭐ formulaire avec éléments .catch-me-if-you-can
├── Dropzone.tsx                # ⭐ react-dropzone wrapper pour SACRED_UPLOAD
├── ErrorCode.tsx               # composant affichant un code HTTP (utilisé par RANDOM_ERROR)
├── FakeUpload/                 # composant fake d'upload (animation, pas de vrai POST)
├── InternalErrorMsg.tsx        # message d'erreur générique
├── Label.tsx                   # label de formulaire
├── Link.tsx                    # wrapper de <a> avec styles
├── Loading.tsx                 # spinner générique
├── LoginForm.tsx               # ⭐ formulaire login + MFA OTP
├── PlusButton.tsx              # bouton + (corsicamon : ajouter à la collection)
├── RandomBibleVerse.tsx        # verset biblique aléatoire
├── RandomLoader.tsx            # ⭐ loader random
├── UploadPreview.tsx           # preview d'un fichier uploadé
└── XButton.tsx                 # bouton X de fermeture
```

⭐ = composant clé pour les scénarios Ocarina.

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

| Mode                   | Comportement                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| Sans OTP               | `onLogin({ withMFA: false, password })`&nbsp;→&nbsp;si OK, authentifié                          |
| Avec OTP, étape&nbsp;1 | `onLogin({ withMFA: true, pre: true, password })`&nbsp;→&nbsp;si OK, fetch `/api/otp?_user=<u>` |
| Avec OTP, étape&nbsp;2 | L'utilisateur tape l'OTP, `onLogin({ withMFA: true, password })`&nbsp;→&nbsp;authentifié        |

### `abortControllerRef`

```tsx
const abortControllerRef = useRef<AbortController | null>(null);

useEffect(() => () => abortControllerRef.current?.abort(), []);

...
abortControllerRef.current?.abort();
abortControllerRef.current = new AbortController();

const response = await fetch(`...`, { signal: abortControllerRef.current.signal });
```

→ Annule une requête en cours quand l'utilisateur clique sur «&nbsp;_Send OTP_&nbsp;» deux fois ou quand le composant est unmounted.

### Validation de schema (réponse service OTP)

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

- **Validation parasite** (un message d'erreur apparaît sur un input correct).
- **Toasts éphémères** (apparaissent puis disparaissent).
- **Formulaire refusé aléatoirement au submit** (message d'erreur incompréhensible et aléatoire).

Côté tests&nbsp;:

1. **`HumanizedDriver`** côté `ocarina-example`&nbsp;: ralentit les saisies, simule frappes/fautes/corrections.
2. **`Watcher` `catch_me_if_you_can_cb`**&nbsp;: détecte les éléments parasites en arrière-plan.

## `Dropzone.tsx`

```tsx
const onDrop = useCallback((acceptedFiles: File[]) => {
  setFiles((prev) => [...prev, ...acceptedFiles]);
}, []);

const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });
```

- Drag-and-drop multi-fichiers.
- Aperçu via `UploadPreview` par fichier.
- Pas de vrai upload, c'est un faux upload (animation, pas de POST).

`tests/scenarios/sacred_upload/upload_files.py`&nbsp;:

- Ouverture de la page,
- Drag d'un fichier fixture,
- Vérification de l'aperçu.

## `RandomLoader.tsx`

```tsx
const LOADERS = [SpinnerStyle1, SpinnerStyle2, SpinnerStyle3, ...] as const;

const RandomLoader = () => {
  const [Loader] = useState(() => pickRandom(LOADERS));
  return <Loader />;
};
```

→ Choisit un loader aléatoire **à la création**. Persiste pendant la durée de vie du composant.

Côté tests&nbsp;: la page `RANDOM_LOADERS` affiche plusieurs `RandomLoader`&nbsp;;&nbsp;le test vérifie juste que _quelque chose_ apparaît. Aucun loader spécifique n'est attendu.

## `Loading.tsx` vs `RandomLoader.tsx`

| `Loading`                                     | `RandomLoader`                |
| --------------------------------------------- | ----------------------------- |
| Spinner fixe (ne change pas)                  | Choisi aléatoirement          |
| Utilisé par `Dashboard` (waiting `isLoading`) | Utilisé par `RANDOM_LOADERS`  |
| Comportement déterministe                     | Comportement non déterministe |

## `ErrorCode.tsx` + `InternalErrorMsg.tsx`

Composants visuels d'erreur. Affichent typiquement «&nbsp;_500 Internal Server Error_&nbsp;». La page `RANDOM_ERROR` utilise ces composants pour _simuler_ une page d'erreur, et le titre est matché par `ERROR_PAGE_REGEX` côté tests.

## `RandomBibleVerse.tsx`

Composant cosmétique&nbsp;: affiche un verset aléatoire. Utile afin que le _Spam God_ veille sur l'Igoristan.

## `BackToHome.tsx` /&nbsp;`BackToSicily.tsx`

Liens de retour à la page d'accueil ou d'envoi sur un site sicilien pour éjecter les envahisseurs. ✈️

## `LoginForm`

`tests/scenarios/dashboard/access/happy_paths.py`&nbsp;:

- `open_dashboard_login_page`,
- `verify_dashboard_login_page`,
- `login_without_otp_and_with_retries` (90% succès, jusqu'à 10 retries pour passer la chance),
- `start_to_login_with_otp_and_with_retries`,
- `verify_otp_screen`,
- `type_otp_with_retries`,
- `verify_dashboard_welcome_page`,
- `click_on_go_to_nested_page_btn`,
- `verify_dashboard_protected_page`.

Soit ~9 acts, soit 2 `drive_page` minimum, parfois 3. C'est le cas le plus _complet_ de la suite canonique.
