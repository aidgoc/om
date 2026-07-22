#!/usr/bin/env bash
# Sync the plugin Stop-hook from the canonical source (plugin/hooks/) to its
# other three homes so all copies stay identical. Run after editing the hook.
#   1. plugin/hooks/                                  <- SOURCE (edit here)
#   2. marketplace/plugins/darshana/hooks/            <- marketplace copy
#   3. ~/.claude/plugins/cache/darshana-marketplace/darshana/*/hooks/  <- installed/live
# Usage: .claude/tools/sync-plugin-hook.sh
set -euo pipefail
cd "$(dirname "$0")/../.."

SRC="plugin/hooks"
DEST_MARKET="marketplace/plugins/darshana/hooks"

cp -v "$SRC"/hooks.json "$SRC"/vritti-check.py "$SRC"/vritti-check.md "$DEST_MARKET"/

for CACHE in "$HOME/.claude/plugins/cache/darshana-marketplace/darshana"/*/hooks; do
  [ -d "$CACHE" ] || continue
  cp -v "$SRC"/hooks.json "$SRC"/vritti-check.py "$SRC"/vritti-check.md "$CACHE"/
done

echo "Hook synced. Restart Claude Code for the installed copy to take effect."
