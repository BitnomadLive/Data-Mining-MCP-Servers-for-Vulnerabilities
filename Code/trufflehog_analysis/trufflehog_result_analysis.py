import os
import json

# Path to the folder containing GitHub repositories
base_path = "/media/sf_MCP/cloned_repos"

# List to store file paths with at least one "Verified": true result
verified_files = []

# Traverse the folder structure
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file == "trufflehog_results.json":
            file_path = os.path.join(root, file)

            print("Currently working on: " + str(file_path))

            # Skip empty files
            if os.path.getsize(file_path) == 0:
                continue

            # Read and process the JSON file
            with open(file_path, "r") as f:
                try:
                    verified_found = False
                    for line in f:
                        data = json.loads(line)
                        if data.get("Verified") == True:
                            verified_found = True
                            break  # No need to check further lines in this file
                    if verified_found:
                        verified_files.append(file_path)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {file_path}")

# Print the files with at least one "Verified: true" result
print("Files with at least one 'Verified: true' result:")
for verified_file in verified_files:
    print(verified_file)

# Print statistics
total_files = len(verified_files)
print(f"\nTotal non-empty files with 'Verified: true' results: {total_files}")
