import os
import re
import json
import pandas as pd
import requests
import ollama
from requests.auth import HTTPBasicAuth
import urllib3
from dotenv import load_dotenv
import csv

# -----------------------
# CONFIGURATION
# -----------------------
BRD_FOLDER = "/Users/automationtesting/BRD-Test-Automation/BRD_files"
OUTPUT_FOLDER = "/Users/automationtesting/BRD-Test-Automation/output"
MODEL = "minimax-m2.5:cloud"
load_dotenv()
# Jira credentials & project key
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # e.g., https://jira.gosi.ins
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")
PROJECT_KEY = "DE"  # Jira project key for Test Sets

auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
VERIFY_SSL = False

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def get_feature_name_from_ai(brd_text):
    """Generate short feature name from BRD using Ollama."""
    prompt = f"""
Read the BRD and return a short feature name (max 5 words).
Return ONLY the name.
BRD:
{brd_text}
"""
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    name = response["message"]["content"].strip()
    name = re.sub(r"[^a-zA-Z0-9_ ]", "", name)
    return name.replace(" ", "_")

def create_test_set(feature_name):
    """Create a Test Set in Jira and return its key."""
    url = f"{JIRA_BASE_URL}/rest/api/2/issue"
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": feature_name,
            "issuetype": {"name": "Test Set"}
        }
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=VERIFY_SSL)
    if response.status_code in [200, 201]:
        testset_key = response.json().get("key")
        print(f"✅ Test Set created: {testset_key}")
        return testset_key
    else:
        raise Exception(f"❌ Failed to create Test Set: {response.status_code} {response.text}")

def call_ollama(brd_text):
    """Generate AI test cases from BRD in standard table format."""
    prompt = f"""
Generate test cases in table format:
Test Case ID | Description | Precondition | Steps | Expected Result | Priority

BRD:
{brd_text}

Return ONLY table rows using | delimiter.
"""
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

def parse_ai_table(ai_output, testset_key):
    """Convert AI table to Xray CSV columns."""
    import pandas as pd
    rows = []

    for line in ai_output.splitlines():
        line = line.strip()
        if not line or line.startswith("|---"):  # skip empty or separator lines
            continue

        # Split and filter out empty strings from leading/trailing pipes
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) != 6:
            print(f"⚠️ Skipping malformed line: {parts}")
            continue

        # Combine Steps + Expected Result into Xray Steps column
        steps_combined = parts[3].replace("\n", "; ") + " | Expected: " + parts[4].replace("\n", "; ")
        row = {
            "Summary": parts[0],
            "Description": parts[1],
            "Test Type": "Manual",
            "Test Set": testset_key,
            "Precondition": parts[2],
            "Steps": steps_combined,
            "Priority": parts[5]
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        print("⚠️ No rows parsed! Check AI output formatting.")
    return df

def save_to_csv(df, feature_name):
    """Save DataFrame to CSV in Xray-compatible format."""
    import csv  # make sure this is imported
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    file_path = os.path.join(OUTPUT_FOLDER, f"{feature_name}_testcases.csv")
    df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)
    print(f"✅ CSV saved: {file_path}")
    return file_path

# -----------------------
# MAIN SCRIPT
# -----------------------
for brd_file in os.listdir(BRD_FOLDER):
    if not brd_file.lower().endswith(".txt"):
        continue
    brd_path = os.path.join(BRD_FOLDER, brd_file)
    with open(brd_path, "r", encoding="utf-8") as f:
        brd_text = f.read()

    # Step 1: Generate feature name
    feature_name = get_feature_name_from_ai(brd_text)

    # Step 2: Create Test Set in Jira
    testset_key = create_test_set(feature_name)

    # Step 3: Generate AI test cases
    ai_output = call_ollama(brd_text)

    # Step 4: Parse AI output to Xray CSV format
    df = parse_ai_table(ai_output, testset_key)

    # Step 5: Save CSV
    save_to_csv(df, feature_name)
    
    ai_output = call_ollama(brd_text)
    print("---- AI Output ----")
    print(ai_output)
    print("-------------------")



# # Allow multiple refinements
# while True:
#     user_prompt = input("\n💡 Enter refinement instructions (or 'done' to finish): ").strip()
#     if user_prompt.lower() == "done" or not user_prompt:
#         break

#     # Build prompt for refining existing test cases
#     refine_prompt = f"""
# The following are AI-generated test cases:
# {ai_output}

# Refine these test cases based on the user instructions below.
# User instructions: {user_prompt}

# Return ONLY updated test cases in the same table format:
# Test Case ID | Description | Precondition | Steps | Expected Result | Priority
# """
#     refined_output = ollama.chat(model=MODEL, messages=[{"role": "user", "content": refine_prompt}])
#     ai_output = refined_output["message"]["content"].strip()

#     print("---- Refined AI Output ----")
#     print(ai_output)

# # Parse final refined output to DataFrame
# df = parse_ai_table(ai_output, testset_key)

# # Save CSV/Excel
# save_to_csv(df, feature_name)


# import os
# import requests
# from requests import auth
# from requests.auth import HTTPBasicAuth
# import urllib3
# import pandas as pd


# # =====================
# # Load .env credentials
# # =====================
# load_dotenv()
# JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # https://jira.gosi.ins
# JIRA_USERNAME = os.getenv("JIRA_USERNAME")  # email
# JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")  # password or API token

# CSV_FILE_PATH = "/Users/automationtesting/BRD-Test-Automation/output/VIC_Registration_testcases.csv"

# if not JIRA_BASE_URL or not JIRA_USERNAME or not JIRA_PASSWORD:
#     raise Exception("⚠️ Missing Jira credentials in .env")

# # =====================
# # Disable SSL warnings
# # =====================
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# VERIFY_SSL = False

# auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)

# # =====================
# # Test Jira connection
# # =====================
# print("🔹 Testing Jira connection...")
# me_url = f"{JIRA_BASE_URL}/rest/api/2/myself"
# r = requests.get(me_url, auth=auth, verify=VERIFY_SSL)
# r.raise_for_status()
# print("✅ Authenticated as:", r.json().get("displayName"))
# # Read the CSV file
# if not os.path.isfile(CSV_FILE_PATH):
#     raise Exception(f"⚠️ CSV file not found: {CSV_FILE_PATH}")

# df = pd.read_csv(CSV_FILE_PATH)

# # Iterate through each test case
# for index, row in df.iterrows():
#     payload = {
#         "fields": {
#             "project": {"key": "YOUR_PROJECT_KEY"},  # Replace with your project key
#             "summary": row['Summary'],
#             "description": row['Description'],
#             "issuetype": {"name": "Test"},  # Assuming you're using the "Test" issue type
#             "customfield_precondition": row['Precondition'],  # Adjust field names as necessary
#             "customfield_steps": row['Steps'],  # Adjust field names as necessary
#             "customfield_priority": row['Priority']  # Adjust field names as necessary
#         }
#     }

#     # Make the API call to create the issue
#     response = requests.post(
#         f"{JIRA_BASE_URL}/rest/api/2/issue",
#         auth=auth,
#         json=payload,
#         verify=False
#     )

#     if response.status_code in [200, 201]:
#         print(f"✅ Test Case created: {response.json().get('key')}")
#     else:
#         print(f"❌ Failed to create Test Case: {response.status_code} {response.text}")