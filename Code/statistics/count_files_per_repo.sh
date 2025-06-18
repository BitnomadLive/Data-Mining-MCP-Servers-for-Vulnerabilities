#!/bin/bash

# Directory containing the cloned repositories
base_dir="/media/sf_MCP/cloned_repos"

# Temporary file to store the intermediate results
temp_file=$(mktemp)

# Loop through each repository
for repo in "$base_dir"/*; do
  if [ -d "$repo" ]; then
    repo_name=$(basename "$repo")
    file_count=$(find "$repo" -type f | wc -l)
    echo "$file_count $repo_name" >> "$temp_file"
  fi
done

# Sort the results in descending order and display them
sort -nr "$temp_file"

# Clean up the temporary file
rm "$temp_file"