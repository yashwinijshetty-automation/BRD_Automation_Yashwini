import ollama
import pandas as pd
import os
import re
import requests
from requests.auth import HTTPBasicAuth

# -------- CONFIG --------
BRD_FOLDER = "/Users/automationtesting/BRD-Test-Automation/BRD_files"
OUTPUT_FOLDER = "/Users/automationtesting/BRD-Test-Automation/output"
MODEL = "minimax-m2.5:cloud"

# Jira credentials from environment variables
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")
auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)

# -------- HELPER FUNCTIONS --------
def call_ollama(brd_text):
    """
    Generate test cases in table format from a BRD using Ollama.
    Returns table rows as string.
    """
    prompt = f"""
Generate test cases in table format:
Test Case ID | Description | Precondition | Steps | Expected Result | Priority

BRD:
{brd_text}

Return ONLY table rows using | delimiter.
"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def get_feature_name_from_ai(brd_text):
    """
    Extract a short feature name (max 5 words) from a BRD using Ollama.
    Returns a string suitable for folder or file naming.
    """
    prompt = f"""
Read BRD and return a short feature name (max 5 words).
Return ONLY the name.
BRD:
{brd_text}
"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    name = response["message"]["content"].strip()
    # Remove non-alphanumeric characters except underscore
    name = re.sub(r"[^a-zA-Z0-9_ ]", "", name)
    # Replace spaces with underscores
    return name.replace(" ", "_")


def parse_ai_table(ai_output):
    """
    Parse the AI-generated table text (pipe-separated) into a DataFrame.
    Handles multiple steps and commas correctly for CSV export.
    """
    rows = []
    for line in ai_output.splitlines():
        if not line.strip():
            continue
        # Split on | but allow multiple spaces around
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 6:
            # Skip invalid lines
            continue
        # Convert steps to semicolon-separated format
        steps = parts[3].replace("\n", "; ").replace(",", ",")
        row = {
            "Test Case ID": parts[0],
            "Description": parts[1],
            "Precondition": parts[2],
            "Steps": steps,
            "Expected Result": parts[4],
            "Priority": parts[5]
        }
        rows.append(row)
    return pd.DataFrame(rows)


def save_to_csv(df, feature_name):
    """
    Save DataFrame to CSV in Xray-compatible format (all fields quoted)
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    file_path = os.path.join(OUTPUT_FOLDER, f"{feature_name}_testcases.csv")
    df.to_csv(file_path, index=False, quoting=pd.io.common.csv.QUOTE_ALL)
    print(f"CSV saved to: {file_path}")


# # -------- MAIN SCRIPT --------
# if __name__ == "__main__":
#     # Test Jira connection
#     try:
#         r = requests.get(f"{JIRA_BASE_URL}/rest/api/2/myself", auth=auth, verify=False)
#         print("Jira connection status:", r.status_code)
#     except Exception as e:
#         print("Jira connection failed:", e)

#     # Process each BRD file
#     for brd_file in os.listdir(BRD_FOLDER):
#         if not brd_file.lower().endswith(".txt"):
#             continue
#         brd_path = os.path.join(BRD_FOLDER, brd_file)
#         with open(brd_path, "r", encoding="utf-8") as f:
#             brd_text = f.read()

#         # Generate feature name
#         feature_name = get_feature_name_from_ai(brd_text)

#         # Generate AI test cases
#         ai_output = call_ollama(brd_text)

#         # Parse into DataFrame
#         df = parse_ai_table(ai_output)

#         # Save to CSV
#         save_to_csv(df, feature_name)