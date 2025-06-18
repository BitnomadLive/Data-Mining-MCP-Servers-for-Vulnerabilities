#!/bin/bash

# Directory containing the cloned repositories
base_dir="/media/sf_MCP/cloned_repos"

# Find all files and extract extensions
find "$base_dir" -type f | awk -F. '
  NF>1 {ext[$NF]++; total++} # Increment count for each file extension and total
  END {
    for (e in ext) {
      printf "%.2f %s\n", (ext[e]/total)*100, e # Print percentage first for sorting
    }
  }
' | sort -nr | awk '
  {printf "%s: %.2f%%\n", $2, $1} # Reformat the output
'
