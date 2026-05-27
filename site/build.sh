#!/usr/bin/env bash
# Production build: Hugo, then Pagefind indexing.
# The Pagefind search only exists after this step (it indexes public/).
set -euo pipefail
cd "$(dirname "$0")"

# baseURL: defaults to "/" for local dev (preview with `pagefind --serve` at root).
# CI sets HUGO_BASEURL to the GitHub Pages URL (e.g. https://user.github.io/repo/).
HUGO_ARGS=(--gc --cleanDestinationDir)
if [ -n "${HUGO_BASEURL:-}" ]; then
  HUGO_ARGS+=(--baseURL "$HUGO_BASEURL")
fi
if [ "${HUGO_MINIFY:-0}" = "1" ]; then
  HUGO_ARGS+=(--minify)
fi

hugo "${HUGO_ARGS[@]}"

# Drop Mermaid: hugo-book ships mermaid.min.js (~3 MB) in its static/,
# Hugo copies it to public/ even though no page uses it.
rm -f public/mermaid.min.js

# Guard: fail loudly if any page still references the purged Mermaid asset
# (e.g. someone added a ```mermaid block or {{< mermaid >}} shortcode).
if grep -rlF 'mermaid.min.js' public --include='*.html' >/dev/null; then
  echo "ERROR: HTML references mermaid.min.js but the asset was purged." >&2
  echo "       Either restore Mermaid or convert the diagram to ASCII." >&2
  grep -rlF 'mermaid.min.js' public --include='*.html' >&2
  exit 1
fi

npx -y pagefind --site public --root-selector "article.book-article" --exclude-selectors "pre"

echo
echo "Build done -> public/"
echo "Preview with search:  npx -y pagefind --site public --serve"
