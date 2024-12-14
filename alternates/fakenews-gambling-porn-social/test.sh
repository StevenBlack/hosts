#!/bin/bash

# Define the file path
FILE_PATH="hosts"

if [ -f "$FILE_PATH" ]; then
  # Use awk to comment out the Reddit block
  awk '
    BEGIN { in_reddit_block = 0 }
    /^# Reddit$/ { in_reddit_block = 1; print "#" $0; next }
    in_reddit_block && $0 == "" { in_reddit_block = 0; print "#" $0; next }
    in_reddit_block { print "#" $0; next }
    { print $0 }
  ' "$FILE_PATH" > "$FILE_PATH.tmp" && mv "$FILE_PATH.tmp" "$FILE_PATH"

  echo "Processing complete. Modified file:"
  cat "$FILE_PATH"
else
  echo "File not found: $FILE_PATH"
  exit 1
fi
