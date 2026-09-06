#!/usr/bin/env bash
# Smoke test every registered non-stack search domain.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$REPO_ROOT/src/ui-ux-pro-max/scripts"
SEARCH="$SCRIPTS_DIR/search.py"
QUERY_OVERRIDE="${1:-}"
EXPECTED_COUNT="${EXPECTED_DOMAIN_COUNT:-12}"

smoke_query() {
  case "$1" in
    style) echo "minimalism ui glassmorphism design" ;;
    color) echo "healthcare app calming trustworthy" ;;
    chart) echo "time series chart trend dashboard" ;;
    landing) echo "hero testimonials cta conversion landing page" ;;
    product) echo "saas dashboard app product" ;;
    ux) echo "accessibility keyboard navigation focus" ;;
    typography) echo "font pairing heading body typography" ;;
    icons) echo "warning icon glyph symbol" ;;
    gsap) echo "gsap scroll reveal stagger animation" ;;
    react) echo "react performance rerender waterfall suspense" ;;
    web) echo "aria form accessibility input outline" ;;
    google-fonts) echo "google font family sans serif variable" ;;
    *) return 1 ;;
  esac
}

if [ ! -f "$SEARCH" ]; then
  echo "FAIL: search.py not found at $SEARCH" >&2
  exit 2
fi

DOMAINS=()
while IFS= read -r line; do
  line="${line%$'\r'}"
  [ -n "$line" ] && DOMAINS+=("$line")
done < <(PYTHONPATH="$SCRIPTS_DIR" python3 -c "
from core import CSV_CONFIG
for domain in CSV_CONFIG:
    print(domain)
")

if [ "${#DOMAINS[@]}" -ne "$EXPECTED_COUNT" ]; then
  echo "FAIL: CSV_CONFIG has ${#DOMAINS[@]} domains, expected $EXPECTED_COUNT" >&2
  echo "      Set EXPECTED_DOMAIN_COUNT after an intentional registry change." >&2
  exit 2
fi

if [ -n "$QUERY_OVERRIDE" ]; then
  echo "Smoke-testing ${#DOMAINS[@]} domains with override query '$QUERY_OVERRIDE':"
else
  echo "Smoke-testing ${#DOMAINS[@]} domains with focused probes:"
fi
fail=0
for domain in "${DOMAINS[@]}"; do
  query="$QUERY_OVERRIDE"
  if [ -z "$query" ]; then
    query=$(smoke_query "$domain" || true)
  fi

  if [ -z "$query" ]; then
    printf '  FAIL  %-14s missing smoke probe\n' "$domain"
    fail=$((fail + 1))
    continue
  fi

  payload=$(python3 "$SEARCH" "$query" --domain "$domain" -n 1 --json 2>/dev/null || true)
  count=$(printf '%s' "$payload" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('count',0) if not data.get('error') else 0)" 2>/dev/null || echo 0)
  if [ "${count:-0}" -gt 0 ]; then
    printf '  PASS  %-14s %d\n' "$domain" "$count"
  else
    diagnostics=$(PYTHONPATH="$SCRIPTS_DIR" python3 -c 'import json,sys; from core import search; print(json.dumps(search(sys.argv[2], domain=sys.argv[1], max_results=1, diagnostics=True).get("diagnostics", {}), sort_keys=True))' "$domain" "$query" 2>/dev/null || true)
    printf '  FAIL  %-14s 0 query=%q diagnostics=%s\n' "$domain" "$query" "${diagnostics:-unavailable}"
    fail=$((fail + 1))
  fi
done

total=${#DOMAINS[@]}
echo
if [ "$fail" -gt 0 ]; then
  echo "FAIL: $fail/$total domains returned 0 results" >&2
  exit 1
fi

echo "OK: $total/$total domains returned ≥1 result"
