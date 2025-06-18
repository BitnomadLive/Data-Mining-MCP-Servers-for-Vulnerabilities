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

def main():
    # Path to the JSON file
    json_file = "github_repos.json"  

    # Path to the folder where repositories will be cloned
    target_folder = "/media/sf_MCP/cloned_repos"  

    # Clone the repositories
    clone_repositories(json_file, target_folder)

if __name__ == "__main__":
    main()
