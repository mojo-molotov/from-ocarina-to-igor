#!/usr/bin/env bash
# One-shot post-clone setup. Idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."

# Activate the repo's git hooks (Prettier on staged markdown, etc.).
# Git won't do this automatically by design (security).
git config core.hooksPath .githooks
echo "git hooks: core.hooksPath -> .githooks"
