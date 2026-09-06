#!/usr/bin/env bash
# Smoke test: every stack registered in STACK_CONFIG must return at least one
# search result for a focused query. Catches registry/CSV regressions early
# (e.g. a stack added to STACK_CONFIG but missing its CSV, or a CSV emptied
# by a botched merge).
#
# Usage:  scripts/smoke-stacks.sh [query]
# Env:    EXPECTED_STACK_COUNT — default 22. Bump deliberately when adding
#         or removing a stack so accidental drift still fails loudly.
#
# Exit codes:
#   0 — all stacks returned ≥1 result
#   1 — at least one stack returned 0 results
#   2 — environment problem (search.py missing, registry size mismatch)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$REPO_ROOT/src/ui-ux-pro-max/scripts"
SEARCH="$SCRIPTS_DIR/search.py"

QUERY_OVERRIDE="${1:-}"
EXPECTED_COUNT="${EXPECTED_STACK_COUNT:-22}"

smoke_query() {
  case "$1" in
    react) echo "React useState for component local state" ;;
    nextjs) echo "Next.js App Router for a new project" ;;
    vue) echo "Vue Composition API for a new project" ;;
    svelte) echo "Svelte 5 \$state rune for reactive state" ;;
    astro) echo "Astro islands architecture interactive components" ;;
    swiftui) echo "SwiftUI @State for view-local value state" ;;
    react-native) echo "functional React Native components" ;;
    flutter) echo "prefer StatelessWidget when Flutter UI has no mutable state" ;;
    nuxtjs) echo "Nuxt file-based page routing" ;;
    nuxt-ui) echo "install the Nuxt UI module" ;;
    html-tailwind) echo "Tailwind z-index utility scale for layered UI" ;;
    shadcn) echo "install shadcn components with the CLI" ;;
    jetpack-compose) echo "pure Jetpack Compose UI composables" ;;
    threejs) echo "Three.js OrbitControls must be imported separately" ;;
    angular) echo "standalone Angular components for a new project" ;;
    laravel) echo "reusable Laravel Blade UI components" ;;
    javafx) echo "launch JavaFX UI from an Application subclass" ;;
    wpf) echo "WPF INotifyPropertyChanged data binding updates" ;;
    winui) echo "WinUI InfoBar for status messages" ;;
    avalonia) echo "Avalonia XAML namespace declaration" ;;
    uno) echo "Uno Platform WinUI XAML API surface" ;;
    uwp) echo "UWP compiled x:Bind data binding" ;;
    *) return 1 ;;
  esac
}

if [ ! -f "$SEARCH" ]; then
  echo "FAIL: search.py not found at $SEARCH" >&2
  exit 2
fi

# Single source of truth: pull stacks from STACK_CONFIG so this script never
# goes stale relative to the registry.
STACKS=()
while IFS= read -r line; do
  line="${line%$'\r'}"  # strip CR on Windows where python's print emits CRLF
  [ -n "$line" ] && STACKS+=("$line")
done < <(PYTHONPATH="$SCRIPTS_DIR" python3 -c "
from core import AVAILABLE_STACKS
for s in AVAILABLE_STACKS:
    print(s)
")

if [ "${#STACKS[@]}" -ne "$EXPECTED_COUNT" ]; then
  echo "FAIL: STACK_CONFIG has ${#STACKS[@]} stacks, expected $EXPECTED_COUNT" >&2
  echo "      Set EXPECTED_STACK_COUNT to override after an intentional change." >&2
  exit 2
fi

if [ -n "$QUERY_OVERRIDE" ]; then
  echo "Smoke-testing ${#STACKS[@]} stacks with override query '$QUERY_OVERRIDE':"
else
  echo "Smoke-testing ${#STACKS[@]} stacks with focused probes:"
fi
fail=0
for s in "${STACKS[@]}"; do
  query="$QUERY_OVERRIDE"
  if [ -z "$query" ]; then
    query=$(smoke_query "$s" || true)
  fi

  if [ -z "$query" ]; then
    printf '  FAIL  %-18s missing smoke probe\n' "$s"
    fail=$((fail + 1))
    continue
  fi

  payload=$(python3 "$SEARCH" "$query" --stack "$s" -n 1 --json 2>/dev/null || true)
  count=$(printf '%s' "$payload" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('count',0) if not data.get('error') else 0)" 2>/dev/null || echo 0)
  if [ "${count:-0}" -gt 0 ]; then
    printf '  PASS  %-18s %d\n' "$s" "$count"
  else
    diagnostics=$(PYTHONPATH="$SCRIPTS_DIR" python3 -c 'import json,sys; from core import search_stack; print(json.dumps(search_stack(sys.argv[2], sys.argv[1], max_results=1, diagnostics=True).get("diagnostics", {}), sort_keys=True))' "$s" "$query" 2>/dev/null || true)
    printf '  FAIL  %-18s 0 query=%q diagnostics=%s\n' "$s" "$query" "${diagnostics:-unavailable}"
    fail=$((fail + 1))
  fi
done

total=${#STACKS[@]}
echo
if [ "$fail" -gt 0 ]; then
  echo "FAIL: $fail/$total stacks returned 0 results" >&2
  exit 1
fi
echo "OK: $total/$total stacks returned ≥1 result"
