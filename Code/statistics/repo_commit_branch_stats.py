import os
import subprocess
import csv
from concurrent.futures import ThreadPoolExecutor


# Function to check if a directory is a valid Git repository
def is_git_repo(repo_path):
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


# Function to get the number of commits and branches for a repository
def get_repo_stats(repo_path):
    try: 
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", repo_path],
            cwd=repo_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )       
        # Check if the directory is a valid Git repository
        if not is_git_repo(repo_path):
            return repo_path, 0, 0

        # Get the number of commits
        commits = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        
        branches = subprocess.check_output(
            ["git", "--no-pager", "branch", "-r"],
            cwd=repo_path,
            stderr=subprocess.DEVNULL,
            text=True
        ).splitlines()

        # count branches
        branch_count = len(branches)

        return repo_path, int(commits), branch_count
    except subprocess.CalledProcessError as e:
        print(f"Error processing repo at {repo_path}: {e}")
        return repo_path, 0, 0


# Function to process all repositories in a folder
def process_repos(folder_path):
    results = []

    # List all subdirectories (potential Git repos)
    repos = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_repo_stats, repo) for repo in repos]
        for future in futures:
            result = future.result()
            if result:
                results.append(result)

    # Sort results by the number of commits in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    return results


# Function to print results in a table format
def print_results(results):
    print("{:<50} {:<15} {:<15}".format("Repository", "Commits", "Branches"))
    for repo, commits, branches in results:
        print(f"{repo:<50} {commits:<15} {branches:<15}")


# Function to write results to a CSV file
def write_to_csv(results, output_csv):
    with open(output_csv, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Repository", "Commits", "Branches"])
        writer.writerows(results)

# Main function
def main():
    # Replace this with your folder path
    folder_path = "/media/sf_MCP/cloned_repos"
    # Output CSV file name
    output_csv = "repo_commit_branch_stats.csv"

    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    print("Processing repositories...")
    results = process_repos(folder_path)

    print("\nResults:")
    print_results(results)

    print(f"\nWriting results to '{output_csv}'...")
    write_to_csv(results, output_csv)
    print("Done!")


# Entry point of the script
if __name__ == "__main__":
    main()
