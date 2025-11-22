#!/usr/bin/env bash

# shellcheck enable=require-variable-braces

set -euo pipefail

# Ensure required tools are installed
for tool in git jq; do
  if ! command -v "${tool}" > /dev/null 2>&1; then
    echo "Error: ${tool} not found in PATH" >&2
    exit 1
  fi
done

# Clear output file
: > stats.out

# Collect "tag:readmeData.json date" pairs for all tags
mapfile -t taglist < <(
  git for-each-ref --sort=creatordate \
    --format='%(refname:short) %(creatordate:short)' refs/tags |
    awk '{print $1 ":readmeData.json " $2}'
)

# Feed all object names into one cat-file process
exec 3< <(printf '%s\n' "${taglist[@]}" | cut -d' ' -f1 | git cat-file --batch)

for line in "${taglist[@]}"; do
  # Extract the date field by removing everything up to the first space
  date=${line#* }

  # Read one header line from fd 3
  if ! read -r -a header_fields <&3; then
    break
  fi

  # Skip if header is incomplete
  if ((${#header_fields[@]} < 3)); then
    continue
  fi

  size=${header_fields[2]}

  # Validate that size is numeric
  if [[ ! "${size}" =~ ^[0-9]+$ ]]; then
    continue
  fi

  # Read exactly ${size} bytes of blob content
  IFS= read -r -N "${size}" blob <&3

  # Consume the newline that follows the blob
  read -r _ <&3 || true

  # Stream parse JSON only if blob is non-empty
  if [[ -z "${blob}" ]]; then
    continue
  fi

  # Stream parse JSON with jq in "raw input" mode to avoid subshell overhead
  jq -nr --arg date "${date}" --argjson blob "${blob}" '
    $blob.base.entries // empty
    | if type=="array" then
        .[] | "\($date),\(.)"
      else
        "\($date),\(.)"
      end
  ' >> stats.out 2> /dev/null || true
done
