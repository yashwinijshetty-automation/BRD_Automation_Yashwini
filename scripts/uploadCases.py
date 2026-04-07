# # import os
# # import requests
# # from requests.auth import HTTPBasicAuth
# # import urllib3
# # from urllib.parse import quote

# # import os
# # import json
# # import requests
# # from requests.auth import HTTPBasicAuth
# # from dotenv import load_dotenv
# # import urllib3

# # # =====================
# # # Load .env credentials
# # # =====================
# # load_dotenv()

# # JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # e.g., https://your-domain.atlassian.net
# # JIRA_USERNAME = os.getenv("JIRA_USERNAME")  # email
# # JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")  # API token

# # PROJECT_KEY = "DE"                # Jira project key
# # PARENT_FOLDER = "GOSI_Super_APP" # Optional parent, can be just for naming
# # FEATURE_NAME = "VIC_Registration" # Feature/Test Set name
# # CSV_FILE_PATH = "/Users/automationtesting/BRD-Test-Automation/output/VIC_Registration_testcases.csv"

# # if not JIRA_BASE_URL or not JIRA_USERNAME or not JIRA_PASSWORD:
# #     raise Exception("⚠️ Missing Jira credentials in .env")

# # # =====================
# # # Disable SSL warnings if needed
# # # =====================
# # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# # VERIFY_SSL = False

# # auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
# # headers = {"Content-Type": "application/json", "Accept": "application/json"}

# # # =====================
# # # Test Jira connection
# # # =====================
# # print("🔹 Testing Jira connection...")
# # me_url = f"{JIRA_BASE_URL}/rest/api/2/myself"
# # r = requests.get(me_url, auth=auth, verify=VERIFY_SSL)
# # r.raise_for_status()
# # print("✅ Authenticated as:", r.json().get("displayName"))

# # # =====================
# # # Upload CSV to Xray
# # # =====================
# # if not os.path.isfile(CSV_FILE_PATH):
# #     raise Exception(f"⚠️ CSV file not found: {CSV_FILE_PATH}")

# # print(f"🔹 Uploading CSV to Xray: {CSV_FILE_PATH}")
# # with open(CSV_FILE_PATH, 'rb') as f:
# #     files = {'file': (os.path.basename(CSV_FILE_PATH), f, 'text/csv')}
# #     xray_csv_url = f"{JIRA_BASE_URL}/rest/raven/2.0/import/execution/csv"
# #     response = requests.post(
# #         xray_csv_url,
# #         files=files,
# #         auth=auth,
# #         verify=VERIFY_SSL
# #     )

# # if response.status_code in [200, 201]:
# #     print("✅ Test cases uploaded successfully!")
# # else:
# #     print("❌ Upload failed:", response.status_code, response.text)

# import os
# import requests
# from requests.auth import HTTPBasicAuth
# import urllib3
# from dotenv import load_dotenv
# import pandas as pd

# # =====================
# # Load .env credentials
# # =====================
# load_dotenv()
# JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")  # https://jira.gosi.ins
# JIRA_USERNAME = os.getenv("JIRA_USERNAME")  # email
# JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")  # password or API token

# PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
# print("Project Key from ENV:", PROJECT_KEY)

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
#             "project": {"key": PROJECT_KEY},
#             "summary": row['Summary'],
#             "description": row['Description'],
#             "issuetype": {"name": "Test"}
#         }
#     }

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

import os
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from dotenv import load_dotenv
import pandas as pd
import re

# =====================
# Load ENV variables
# =====================
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
CSV_FILE_PATH = "/Users/automationtesting/BRD-Test-Automation/output/VIC_Registration_testcases.csv"

# =====================
# Disable SSL warnings
# =====================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
VERIFY_SSL = False

auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
headers = {"Content-Type": "application/json", "Accept": "application/json"}

# =====================
# Test Jira connection
# =====================
print("🔹 Testing Jira connection...")
resp = requests.get(f"{JIRA_BASE_URL}/rest/api/2/myself", auth=auth, verify=VERIFY_SSL)
resp.raise_for_status()
print("✅ Connected as:", resp.json()["displayName"])

# =====================
# Load CSV
# =====================
print("🔹 Loading CSV...")
df = pd.read_csv(CSV_FILE_PATH, encoding="utf-8", engine="python")
df.columns = df.columns.str.replace('"','').str.strip()
df = df[df["Summary"] != "Test Case ID"]
df = df.fillna("")
print("Columns:", df.columns.tolist())
print("Rows:", len(df))

# =====================
# Step parser
# =====================
def parse_steps(text):
    steps=[]
    expected=""
    if "| Expected:" in text:
        step_part, expected = text.split("| Expected:")
    else:
        step_part = text
    raw_steps = re.split(r'\d+\.', step_part)
    for s in raw_steps:
        s=s.strip()
        if s:
            steps.append(s)
    return steps, expected.strip()

# =====================
# Start Import
# =====================
for index, row in df.iterrows():
    summary = row["Summary"]
    description = row["Description"]
    priority = row["Priority"]
    steps_text = row["Steps"]
    testset_key = row["Test Set"]
    precondition = row["Precondition"]

    print("\n🚀 Creating Test:", summary)

    # -------------------
    # Create Test
    # -------------------
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Test"},
            "priority": {"name": priority}
        }
    }

    r = requests.post(
        f"{JIRA_BASE_URL}/rest/api/2/issue",
        auth=auth,
        headers=headers,
        json=payload,
        verify=VERIFY_SSL
    )

    if r.status_code not in [200,201]:
        print("❌ Test creation failed:", r.text)
        continue

    test_key = r.json()["key"]
    print("✅ Test created:", test_key)

    # -------------------
    # Create Precondition
    # -------------------
    if precondition:
        pre_payload = {
            "fields": {
                "project": {"key": PROJECT_KEY},
                "summary": f"Precondition for {summary}",
                "description": precondition,
                "issuetype": {"name": "Pre-Condition"}  # ⚠️ exact name from your Jira
            }
        }

        pre_resp = requests.post(
            f"{JIRA_BASE_URL}/rest/api/2/issue",
            auth=auth,
            headers=headers,
            json=pre_payload,
            verify=VERIFY_SSL
        )

        if pre_resp.status_code in [200,201]:
            pre_key = pre_resp.json()["key"]
            print("   ➜ Precondition created:", pre_key)

            link_pre = requests.post(
                f"{JIRA_BASE_URL}/rest/raven/2.0/api/test/{test_key}/precondition",
                auth=auth,
                headers=headers,
                json={"add":[pre_key]},
                verify=VERIFY_SSL
            )

            if link_pre.status_code in [200,201]:
                print("   ➜ Precondition linked")
            else:
                print("   ❌ Precondition link failed:", link_pre.text)
        else:
            print("   ❌ Precondition creation failed:", pre_resp.text)

    # -------------------
    # Add Steps
    # -------------------
    steps, expected = parse_steps(steps_text)
    for step in steps:
        step_payload = {
            "step": step,
            "data": "",
            "result": expected
        }

        step_resp = requests.post(
            f"{JIRA_BASE_URL}/rest/raven/2.0/api/test/{test_key}/steps",
            auth=auth,
            headers=headers,
            json=step_payload,
            verify=VERIFY_SSL
        )

        if step_resp.status_code in [200,201]:
            print("   ➜ Step added:", step)
        else:
            print("   ❌ Step error:", step_resp.status_code, step_resp.text)

    # -------------------
    # Link Test Set
    # -------------------
    if testset_key:
        link_resp = requests.post(
            f"{JIRA_BASE_URL}/rest/raven/2.0/api/testset/{testset_key}/test",
            auth=auth,
            headers=headers,
            json={"add":[test_key]},
            verify=VERIFY_SSL
        )

        if link_resp.status_code in [200,201]:
            print("   ➜ Linked to Test Set:", testset_key)
        else:
            print("   ❌ TestSet link failed:", link_resp.status_code, link_resp.text)

print("\n🎉 Import Completed")