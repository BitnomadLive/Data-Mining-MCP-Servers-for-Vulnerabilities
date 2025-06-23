import os
import subprocess
import json
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys

# Paths
OUTPUT_FOLDER = "output"
REPO_FOLDER = "/media/sf_MCP/cloned_repos"  # Folder containing all pre-downloaded repositories
PROGRESS_FILE = "progress.json"
OPENGREP_BINARY = "/home/vboxuser/opengrep/opengrep_manylinux_x86"
OPENGREP_RULES = "/home/vboxuser/opengrep/opengrep-rules"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Track processed repositories
processed_repos = set()

def load_progress():
    """Load progress from the progress file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_progress():
    """Save progress to the progress file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(processed_repos), f)

def signal_handler(sig, frame):
    """Handle interruption signals (e.g., Ctrl+C)."""
    print("\nPausing... Saving progress.")
    save_progress()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def run_opengrep_on_batch(batch, batch_index):
    """Run opengrep on a batch of repositories."""
    output_file = os.path.join(OUTPUT_FOLDER, f"batch_{batch_index}.json")
    print(f"Running opengrep on batch {batch_index}...")
    subprocess.run([
        OPENGREP_BINARY,
        "scan",
        f"--sarif-output={output_file}",
        "-f", OPENGREP_RULES,
        *batch
    ], check=True)

def batch_repositories(repos, batch_size):
    """Yield successive batches of repositories."""
    for i in range(0, len(repos), batch_size):
        yield repos[i:i + batch_size]

# Load progress
processed_repos = load_progress()

# Get list of all repositories in the local folder
all_repos = [os.path.join(REPO_FOLDER, repo) for repo in os.listdir(REPO_FOLDER) if os.path.isdir(os.path.join(REPO_FOLDER, repo))]

# Filter out already processed repositories
remaining_repos = [repo for repo in all_repos if repo not in processed_repos]

BATCH_SIZE = 40

# Process remaining repositories in batches
for batch_index, batch in enumerate(batch_repositories(remaining_repos, BATCH_SIZE), start=1):
    process_batch = False

    # Skip batches that are already processed
    for repo in batch:
        if repo not in processed_repos:
            process_batch = True
            break

    if not process_batch:
        print(f"Skipping already processed batch {batch_index}")
        continue

    try:
        run_opengrep_on_batch(batch, batch_index)
        processed_repos.update(batch)
        save_progress()
    except subprocess.CalledProcessError as e:
        print(f"Error running opengrep on batch {batch_index}: {e}")

print("All repositories processed.")
if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
