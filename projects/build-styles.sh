#!/usr/bin/env sh
# Regenerates each sample's precompiled styles.css so the pages render offline.
# Run after editing a sample's index.html or tailwind.config.js.
set -e
cd "$(dirname "$0")"
for dir in */; do
  [ -f "$dir/tailwind.config.js" ] || continue
  # Pinned to Tailwind v3, the version the original Play CDN builds used.
  (cd "$dir" && npx --yes tailwindcss@3.4.19 -c tailwind.config.js -o styles.css --minify)
done
