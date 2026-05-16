#!/usr/bin/env bash
set -euo pipefail
LC_ALL=C
export LC_ALL

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Manipulate and filter wordlists using standard Unix tools.

Options:
  -i FILE       Input wordlist (default: stdin)
  -o FILE       Output file (default: stdout)
  -d            Deduplicate lines
  -s            Sort alphabetically
  -l MIN:MAX    Filter lines by length range (e.g. 8:16)
  -u            Convert to uppercase
  -L            Convert to lowercase
  -c CHAR       Keep only lines containing CHAR
  -x PATTERN    Exclude lines matching grep pattern
  -m N          Limit output to first N lines
  -S            Print stats only (total, unique, avg length)
  -h            Show this help

Examples:
  $(basename "$0") -i rockyou.txt -d -s -l 8:16 -o filtered.txt
  cat hashes.txt | $(basename "$0") -d -s
  $(basename "$0") -i words.txt -S
EOF
    exit 0
}

INPUT=""
OUTPUT=""
DO_DEDUP=false
DO_SORT=false
LENGTH_MIN=""
LENGTH_MAX=""
DO_UPPER=false
DO_LOWER=false
FILTER_CHAR=""
EXCLUDE_PAT=""
LIMIT=""
STATS_ONLY=false

while getopts "i:o:dsl:uLc:x:m:Sh" opt; do
    case "$opt" in
        i) INPUT="$OPTARG" ;;
        o) OUTPUT="$OPTARG" ;;
        d) DO_DEDUP=true ;;
        s) DO_SORT=true ;;
        l)
            LENGTH_MIN="${OPTARG%%:*}"
            LENGTH_MAX="${OPTARG##*:}"
            ;;
        u) DO_UPPER=true ;;
        L) DO_LOWER=true ;;
        c) FILTER_CHAR="$OPTARG" ;;
        x) EXCLUDE_PAT="$OPTARG" ;;
        m) LIMIT="$OPTARG" ;;
        S) STATS_ONLY=true ;;
        h) usage ;;
        *) echo "Unknown option: -$OPTARG" >&2; exit 2 ;;
    esac
done

if [[ -n "$INPUT" && ! -f "$INPUT" ]]; then
    echo "Error: input file not found: $INPUT" >&2
    exit 2
fi

read_input() {
    if [[ -n "$INPUT" ]]; then
        cat "$INPUT"
    else
        cat
    fi
}

if $STATS_ONLY; then
    read_input | awk '
    BEGIN { total=0; chars=0 }
    { total++; chars += length($0) }
    END {
        avg = (total > 0) ? chars/total : 0
        printf "Total lines:  %d\n", total
        printf "Avg length:   %.1f\n", avg
    }'
    # unique count requires a second pass; reads file again (not usable with stdin)
    unique=$(read_input | sort | uniq | wc -l)
    echo "Unique lines: $unique"
    exit 0
fi

run_pipeline() {
    local data
    data=$(read_input)

    if [[ -n "$LENGTH_MIN" || -n "$LENGTH_MAX" ]]; then
        local min="${LENGTH_MIN:-0}"
        local max="${LENGTH_MAX:-99999}"
        data=$(echo "$data" | awk -v mn="$min" -v mx="$max" 'length >= mn && length <= mx')
    fi

    if [[ -n "$FILTER_CHAR" ]]; then
        data=$(echo "$data" | grep -F -- "$FILTER_CHAR" || true)
    fi

    if [[ -n "$EXCLUDE_PAT" ]]; then
        data=$(echo "$data" | grep -Ev -- "$EXCLUDE_PAT" || true)
    fi

    if $DO_LOWER; then
        data=$(echo "$data" | tr '[:upper:]' '[:lower:]')
    elif $DO_UPPER; then
        data=$(echo "$data" | tr '[:lower:]' '[:upper:]')
    fi

    if $DO_DEDUP; then
        data=$(echo "$data" | sort -u)
    elif $DO_SORT; then
        data=$(echo "$data" | sort)
    fi

    if [[ -n "$LIMIT" ]]; then
        data=$(echo "$data" | head -n "$LIMIT")
    fi

    echo "$data"
}

result=$(run_pipeline)

if [[ -n "$OUTPUT" ]]; then
    echo "$result" > "$OUTPUT"
    echo "Written to $OUTPUT" >&2
else
    echo "$result"
fi
