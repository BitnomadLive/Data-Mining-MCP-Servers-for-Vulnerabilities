# Data-Mining-MCP-Servers-for-Vulnerabilities
Data-Mining MCP Servers for Vulnerabilities
Introduction/motivation
detailed steps so it can be reproduced

## Downloading MCP Servers
First we need to download MCP Server github repos:
```python
import os
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_repo_accessible(github_link):
    """Check if a GitHub repository is accessible without authentication."""
    try:
        subprocess.run(
            ["git", "ls-remote", github_link],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}  # Disable password prompt
        )
        return True
    except subprocess.CalledProcessError:
        return False


def clone_repository(github_link, target_folder):
    """Clone a single repository."""
    repo_name = os.path.basename(github_link.rstrip('/'))
    target_path = os.path.join(target_folder, repo_name)
    try:
        subprocess.run(
            ["git", "clone", github_link, target_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def process_repository(github_link, target_folder):
    """Check if the repository is accessible and clone it if it is."""
    if is_repo_accessible(github_link):
        if clone_repository(github_link, target_folder):
            return "cloned", github_link
        else:
            return "failed", github_link
    else:
        return "inaccessible", github_link


def clone_repositories(json_file, target_folder, max_workers=40):
    """Read repositories from JSON and process them in threads."""
    # Ensure the target folder exists
    os.makedirs(target_folder, exist_ok=True)

    # Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Lists to track results
    inaccessible_repos = []
    cloned_repos = []
    failed_repos = []

    # Total repositories
    total_repos = len(data)

    # Process repositories in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_repository, repo["github_link"], target_folder): repo["github_link"]
            for repo in data
        }

        # Process results as they complete
        for index, future in enumerate(as_completed(futures), start=1):
            github_link = futures[future]
            try:
                status, repo_link = future.result()
                if status == "cloned":
                    cloned_repos.append(repo_link)
                    print(f"[{index}/{total_repos}] Successfully cloned: {repo_link}")
                elif status == "inaccessible":
                    inaccessible_repos.append(repo_link)
                    print(f"[{index}/{total_repos}] Inaccessible (requires authentication): {repo_link}")
                elif status == "failed":
                    failed_repos.append(repo_link)
                    print(f"[{index}/{total_repos}] Failed to clone: {repo_link}")
            except Exception as e:
                print(f"[{index}/{total_repos}] Error processing {github_link}: {e}")

    # Print results
    print("\nCloning process completed.\n")
    print("Statistics:")
    print(f"Total repositories: {total_repos}")
    print(f"Successfully cloned: {len(cloned_repos)}")
    print(f"Inaccessible repositories: {len(inaccessible_repos)}")
    print(f"Failed to clone: {len(failed_repos)}")

    if inaccessible_repos:
        print("\nInaccessible repositories:")
        for repo in inaccessible_repos:
            print(f"- {repo}")

    if failed_repos:
        print("\nFailed repositories:")
        for repo in failed_repos:
            print(f"- {repo}")


if __name__ == "__main__":
    # Path to the JSON file
    json_file = "github_repos.json"  

    # Path to the folder where repositories will be cloned
    target_folder = "/media/sf_MCP/cloned_repos" 

    # Clone the repositories
    clone_repositories(json_file, target_folder)

```

Before starting to hunt for vulnerabilities lets get a overview of our dataset.
Lets start of by getting some simple statistics:

Total Number of repos: 3795

run 
overall_file_type_count_and_percentage.sh
```bash
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
```
output in https://github.com/BitnomadLive/Data-Mining-MCP-Servers-for-Vulnerabilities/blob/main/Code/statistics/overall_file_type_count_and_precentage_output.txt

| file extension | count |
| --- | ---|
| ts | 54774 (14.67%) |
| sample | 53148 (14.23%) |
| js | 52284 (14.00%) |
| py | 24883 (6.66%) |
| json | 23247 (6.23%) |
| md | 22260 (5.96%) |
| map | 14365 (3.85%) |
| go | 6733 (1.80%) |
| pyc | 4559 (1.22%) |
| gitignore | 3937 (1.05%) |

run 
count_files_per_repo.sh > count_files_per_repo_output.txt
```bash
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
```
Output in https://raw.githubusercontent.com/BitnomadLive/Data-Mining-MCP-Servers-for-Vulnerabilities/refs/heads/main/Code/statistics/count_files_per_repo_output.txt
Generate image of the distribution of file counts across repositories
```python
import matplotlib.pyplot as plt
from collections import Counter

def read_file_counts(file_path):
    """
    Reads the file counts and repository names from a text file.
    Args:
        file_path (str): Path to the input file.
    Returns:
        list: A list of file counts (integers).
    """
    file_counts = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                # Split the line into file count and repository name
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    file_count = int(parts[0])  # Convert file count to integer
                    file_counts.append(file_count)
    except Exception as e:
        print(f"Error reading file: {e}")
    return file_counts

def plot_file_distribution_bar_chart(file_counts, output_image):
    """
    Plots a bar chart of file counts across repositories.
    Args:
        file_counts (list): A list of file counts (integers).
        output_image (str): Path to save the output image.
    """
    # Count the number of repositories for each unique file count
    count_distribution = Counter(file_counts)

    # Sort the data by file count
    sorted_counts = sorted(count_distribution.items())

    # Extract data for the bar chart
    x_labels = [str(file_count) for file_count, _ in sorted_counts]
    y_values = [repo_count for _, repo_count in sorted_counts]

    # Create the bar chart
    plt.figure(figsize=(30, 10))  # Increase figure size for better readability
    bar_width = 0.8  # Adjust bar width based on number of bars
    plt.bar(x_labels, y_values, color="skyblue", edgecolor="black", width=bar_width)

    # Adjust X-axis labels for readability
    plt.xticks(range(len(x_labels)), x_labels, rotation=45, ha="right", fontsize=6)  # Smaller font size

    # Add labels and title
    plt.xlabel("Number of Files", fontsize=14)
    plt.ylabel("Number of Repositories", fontsize=14)
    plt.title("Distribution of File Counts Across Repositories", fontsize=16)
    plt.tight_layout()

    # Save the image
    plt.savefig(output_image, dpi=300)
    print(f"Bar chart image saved as {output_image}")

    # Show the plot (optional)
    plt.show()

def main():
    """
    Main function to read data and generate the bar chart.
    """
    # Path to the input file
    input_file = "count_files_per_repo_output.txt"
    
    # Output image path
    output_image = "file_distribution_bar_chart_no_bins.png"
    
    # Read the file counts from the file
    file_counts = read_file_counts(input_file)
    
    # Check if data was successfully read
    if file_counts:
        # Call the function to plot the bar chart
        plot_file_distribution_bar_chart(file_counts, output_image)
    else:
        print("No data to plot. Please check the input file.")

# Call the main function
if __name__ == "__main__":
    main()
```

python 3 generate_distribution_image.py

![alt text](https://raw.githubusercontent.com/BitnomadLive/Data-Mining-MCP-Servers-for-Vulnerabilities/refs/heads/main/Code/statistics/file_distribution_bar_chart_no_bins.png "Distribution of File Counts across Repositories")

Todo: EXPLAIN IMAGE

To achieve that first all README.md files will be converted to vectors and afterward will be clustered with the DBSCAN algorithm. 
DBSCAN (Density-Based Spatial Clustering of Applications with Noise) is a clustering algorithm that groups data points based on density. It identifies clusters as regions of high point density separated by areas of low density. The algorithm requires two key parameters: eps (the maximum distance between two points to be considered neighbors) and minPts (the minimum number of points required to form a dense region). DBSCAN classifies points as core points (dense region centers), border points (on the edge of clusters), or noise points (outliers). It is particularly effective for discovering clusters of arbitrary shapes and handling noise.

Additionally we will output the number of clusters and the amount of repos in each cluster. The similarity between the README files is calculated using cosine similarity by creating a similarity matrix, where each row and column entry hold the value of the similarity between two README files. That similarity matrix is converted into a csv file (output_cytoscape.csv) and written to disc. Moreover all README files that did not fit any cluster are also writen to disc into a file called output_with_unclustered.csv 

```python
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

# Function to read README.md files from the root of each repository
def read_readme_files(folder_path):
    repo_readmes = {}
    for repo_name in os.listdir(folder_path):
        repo_path = os.path.join(folder_path, repo_name)
        if os.path.isdir(repo_path):  # Ensure it's a directory
            readme_path = os.path.join(repo_path, "README.md")  # Check for README.md in the root
            if os.path.isfile(readme_path):  # Only add if README.md exists
                with open(readme_path, "r", encoding="utf-8", errors="ignore") as file:
                    repo_readmes[repo_path] = file.read()
    return repo_readmes

# Main script
def main():
    # Folder containing GitHub repositories
    folder_path = "/media/sf_MCP/cloned_repos"  # Updated path

    # Step 1: Read README.md files
    repo_readmes = read_readme_files(folder_path)
    repo_names = list(repo_readmes.keys())
    readme_texts = list(repo_readmes.values())

    # Step 2: Vectorize README.md content
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(readme_texts)

    # Step 3: Perform DBSCAN clustering
    dbscan = DBSCAN(metric="cosine", eps=0.49, min_samples=2)
    cluster_labels = dbscan.fit_predict(tfidf_matrix)

    # Step 4: Calculate pairwise cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Step 5: Generate Cytoscape-compatible CSV (no bidirectional duplicates)
    rows = []
    for i in range(len(repo_names)):
        for j in range(i + 1, len(repo_names)):  # Only consider pairs (i, j) where i < j
            if cluster_labels[i] == cluster_labels[j] and cluster_labels[i] != -1:
                rows.append({
                    "start_node": i,
                    "githubrepo_of_start_node": repo_names[i],
                    "end_node": j,
                    "githubrepo_of_end_node": repo_names[j],
                    "similarity_score": similarity_matrix[i, j],
                })

    # Save to CSV
    output_csv = "output_cytoscape.csv"
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(f"Output saved to {output_csv}")

    # Step 6: Print the number of clusters, the number of repositories in each cluster, and up to 5 repositories per cluster
    clusters = defaultdict(list)
    unclustered_repos = []  # List to store unclustered repositories

    for idx, label in enumerate(cluster_labels):
        if label == -1:  # Noise points
            unclustered_repos.append(repo_names[idx])
        else:
            clusters[label].append(repo_names[idx])

    total_repos_in_clusters = sum(len(repos) for repos in clusters.values())
    print(f"\nTotal number of repositories: {len(repo_names)}")
    print(f"Total number of repositories in clusters: {total_repos_in_clusters}")
    print(f"Number of clusters found: {len(clusters)}")

    for cluster_label, repos in clusters.items():
        print(f"\nCluster {cluster_label}: {len(repos)} repositories")
        print("  Example repositories:")
        for repo in repos[:5]:  # Print up to 5 repositories per cluster
            print(f"    {repo}")

    # Step 7: Print unclustered repositories
    print(f"\nNumber of unclustered repositories: {len(unclustered_repos)}")
    print("Unclustered repositories:")
    for repo in unclustered_repos:
        print(f"    {repo}")

    # Step 8: Save unclustered repositories to the CSV
    unclustered_rows = [{"githubrepo": repo, "cluster": "unclustered"} for repo in unclustered_repos]
    clustered_rows = [
        {"githubrepo": repo, "cluster": cluster_label}
        for cluster_label, repos in clusters.items()
        for repo in repos
    ]

    # Combine clustered and unclustered data
    output_csv_all = "output_with_unclustered.csv"
    pd.DataFrame(clustered_rows + unclustered_rows).to_csv(output_csv_all, index=False)
    print(f"Output with unclustered repositories saved to {output_csv_all}")


if __name__ == "__main__":
    main()
```

Multiple eps values were tried to get the most amount of clusters:

| Clusters | eps |
| --- | --- |
| 375 |	0.4 |
| 418 | 0.45 |
| 422 | 0.47 |
| 427 | 0.49 |
| 425 | 0.5 |
| 409 | 0.52 |
| 378 | 0.55 |
| 302 | 0.6 |

Talk about cluster amount and results. show biggest 10 clusters


To visualize the the output cytoscape was used

1.  Open cytoscape -> Import -> Network from file -> select output_cytoscape.csv
2. change source descriptio and target description to be source node attributes or target node attributes (picture)
3.  Click ok to import
4. Layout  -> Edge weighted Spring Embedded Layout -> Similarity

   picture of clusters. look into interactive version with cytoscape.js
   

