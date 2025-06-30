import os
import subprocess

# Define the Trufflehog function
def run_trufflehog(repo_path):
    """
    Run Trufflehog against a given repository.
    """
    try:
        # Path to the Trufflehog executable
        trufflehog_path = "/home/vboxuser/Tools/trufflehog"  # path to folder containing repos

        # Trufflehog flags
        results_flag = "--results=verified,unknown"
        json_flag = "--json"

        # Build the Trufflehog command
        command = [
            trufflehog_path,
            "git",
            f"file://{repo_path}",
            results_flag,
            json_flag
        ]

        # Run the command and capture the output
        print(f"Running Trufflehog on: {repo_path}")
        result = subprocess.run(command, text=True, capture_output=True)

        # Check for errors in the output
        if result.returncode != 0:
            print(f"Error running Trufflehog on {repo_path}: {result.stderr}")
        else:
            # Save the output to a file
            output_file = os.path.join(repo_path, "trufflehog_results.json")
            with open(output_file, "w") as f:
                f.write(result.stdout)
            print(f"Trufflehog results saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred while processing {repo_path}: {e}")


# Main function
def main():
    """
    Main function to execute Trufflehog sequentially on a list of repositories,
    resuming from the last checked repository.
    """
    # Path to the directory containing cloned repositories
    repos_dir = "/media/sf_MCP/cloned_repos"

    # Last successfully checked repository/first repo to check
    last_checked_repo = "100ms-spl-token-sniper-mcp"

    # Get a list of repositories in the directory
    repos = [os.path.join(repos_dir, repo) for repo in os.listdir(repos_dir) if os.path.isdir(os.path.join(repos_dir, repo))]

    # Sort repositories alphabetically to ensure consistent order
    repos.sort()

    # Flag to indicate when to start processing
    start_processing = False

    for repo in repos:
        # Check if we should skip to the last checked repository
        if not start_processing:
            if os.path.basename(repo) == last_checked_repo:
                start_processing = True  # Start processing from this repository
            else:
                print(f"Skipping already processed repository: {repo}")
                continue

        # Run Trufflehog on the current repository
        run_trufflehog(repo)


if __name__ == "__main__":
    main()
