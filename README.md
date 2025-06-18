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

TODO
Total Number of repos: 3795

![alt text](https://raw.githubusercontent.com/BitnomadLive/Data-Mining-MCP-Servers-for-Vulnerabilities/refs/heads/main/Code/statistics/file_distribution_bar_chart_no_bins.png "Distribution of File Counts across Repositories")


To achieve that first all README.md files will be converted to vectors and afterward will be clustered with the DBSCAN algorithm. Additionally we will output the number of clusters and the amount of repos in each cluster. The similarity between the README files is calculated using cosine similarity by creating a similarity matrix, where each row and column entry hold the value of the similarity between two README files. That similarity matrix is converted into a csv file (output_cytoscape.csv) and written to disc. Moreover all README files that did not fit any cluster are also writen to disc into a file called output_with_unclustered.csv 

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

Explain eps parameter of DBSCAN

dbscan = DBSCAN(metric="cosine", eps=0.49, min_samples=2)

Clusters  / eps:


425	0.5
302	0.6
375	0.4
418	0.45
378	0.55
409	0.52
422	0.47
427	0.49

