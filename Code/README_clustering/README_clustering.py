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
        print("  Repositories:")
        for repo in repos:
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
