import json
import os
from collections import Counter

# Path to the folder containing the result files
folder_path = "output"

# Initialize a dictionary to store rule details (name, text, and count)
rule_details = {}

# Process all JSON files in the folder
try:
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # Only process files with a .json extension
        if file_name.endswith(".json"):
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)

                # Traverse the JSON structure to count rule names containing "security"
                runs = data.get("runs", [])
                for run in runs:
                    results = run.get("results", [])
                    for result in results:
                        rule_id = result.get("ruleId", "Unknown Rule")
                        rule_text = result.get("message", {}).get("text", "No description provided.")
                        
                        # Only consider rule names containing "security"
                        if "security" in rule_id.lower():
                            if rule_id not in rule_details:
                                rule_details[rule_id] = {"text": rule_text, "count": 0}
                            rule_details[rule_id]["count"] += 1

            except json.JSONDecodeError:
                print(f"Error: File '{file_name}' is not a valid JSON file. Skipping.")
            except Exception as e:
                print(f"Error while processing file '{file_name}': {e}")
except FileNotFoundError:
    print(f"Error: Folder '{folder_path}' not found.")
    exit(1)
except Exception as e:
    print(f"Error while accessing the folder: {e}")
    exit(1)

# Sort the rules by count in descending order
sorted_rules = sorted(rule_details.items(), key=lambda x: x[1]["count"], reverse=True)

# Print the rule names, counts, and their text descriptions
print("Rule Name Counts and Descriptions (Containing 'security', Descending):")
for rule, details in sorted_rules:
    print(f"Rule ID: {rule}")
    print(f"Count: {details['count']}")
    print(f"Description: {details['text']}")
    print("-" * 50)
