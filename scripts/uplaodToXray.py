from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from urllib.parse import quote

# =====================
# Load config
# =====================
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")

PROJECT_KEY = "QA"         # Jira project for Test Sets / issues
REPOSITORY_KEY = "DE"      # Xray test repository (project key)
PARENT_FOLDER = "GOSI_Super_APP"

feature_name = "Dummy_Feature_Upload"
csv_file_path = "/Users/automationtesting/BRD-Test-Automation/output/VIC_Registration/VIC_Registration.csv"

if not JIRA_BASE_URL or not JIRA_USERNAME or not JIRA_PASSWORD:
    raise Exception("⚠️ Missing Jira credentials in .env")

print("🔹 Jira Base URL:", JIRA_BASE_URL)

# =====================
# HTTP setup
# =====================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
VERIFY_SSL = False

auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# =====================
# Test connection
# =====================
print("🔹 Testing Jira connection...")
me_url = f"{JIRA_BASE_URL}/rest/api/2/myself"
r = requests.get(me_url, auth=auth, verify=VERIFY_SSL)
r.raise_for_status()
print("✅ Authenticated as:", r.json().get("displayName"))

# =====================
# Xray helpers
# =====================
def get_root_folders(repository):
    url = f"{JIRA_BASE_URL}/rest/raven/1.0/api/testrepository/{repository}"
    r = requests.get(url, headers=headers, auth=auth, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.json()

def find_root_folder_by_name(repository, folder_name):
    data = get_root_folders(repository)
    for f in data.get("folders", []):
        if f.get("name") == folder_name:
            return f
    return None

def list_repository_folder(repository, folder_path=None):
    if folder_path:
        safe_path = quote(folder_path)
        url = f"{JIRA_BASE_URL}/rest/raven/1.0/api/testrepository/{repository}/{safe_path}"
    else:
        url = f"{JIRA_BASE_URL}/rest/raven/1.0/api/testrepository/{repository}"

    r = requests.get(url, headers=headers, auth=auth, verify=VERIFY_SSL)

    print("🔍 URL:", url)
    print("🔍 Status:", r.status_code)

    if r.status_code == 404:
        return None

    r.raise_for_status()
    return r.json()

def create_folder_by_parent_id(repository, parent_id, folder_name):
    url = f"{JIRA_BASE_URL}/rest/raven/1.0/api/testrepository/{repository}/{parent_id}"
    payload = {"name": folder_name}

    r = requests.post(url, headers=headers, auth=auth, json=payload, verify=VERIFY_SSL)
    r.raise_for_status()

    data = r.json()
    print(f"✅ Folder '{folder_name}' created under parent ID '{parent_id}'")
    return data.get("key") or data.get("id")

def upload_csv_to_folder(repository, folder_path, csv_file):
    url = f"{JIRA_BASE_URL}/rest/raven/2.0/import/execution/csv"
    params = {
        "testRepositoryKey": repository,
        "folder": folder_path
    }

    with open(csv_file, "rb") as f:
        files = {"file": (os.path.basename(csv_file), f, "text/csv")}
        r = requests.post(
            url,
            auth=auth,
            files=files,
            params=params,
            headers={"Accept": "application/json"},
            verify=VERIFY_SSL
        )

    if r.ok:
        print(f"✅ CSV uploaded successfully to '{folder_path}'")
    else:
        raise Exception(f"❌ CSV upload failed: {r.status_code} {r.text}")

# =====================
# Main execution
# =====================
print("🔹 Starting Jira/Xray upload...")

# 1️⃣ Find root parent folder (robust for Xray Server/DC)
parent = find_root_folder_by_name(REPOSITORY_KEY, PARENT_FOLDER)
if not parent:
    raise Exception(f"❌ Parent folder '{PARENT_FOLDER}' does not exist in repository '{REPOSITORY_KEY}'")

parent_id = parent["id"]
print("✅ Parent folder found:", parent_id, parent["name"])

# 2️⃣ Ensure feature folder exists
folder_path = f"{PARENT_FOLDER}/{feature_name}"
feature_data = list_repository_folder(REPOSITORY_KEY, folder_path)

if not feature_data:
    print(f"📁 Feature folder '{feature_name}' not found, creating...")
    create_folder_by_parent_id(REPOSITORY_KEY, parent_id, feature_name)
else:
    print(f"⚠️ Feature folder '{feature_name}' already exists")

# 3️⃣ Upload CSV to correct folder path
upload_csv_to_folder(REPOSITORY_KEY, folder_path, csv_file_path)

print("🎉 Jira/Xray upload complete!")

def get_root_folders(repository):
    urls_to_try = [
        f"{JIRA_BASE_URL}/rest/raven/1.0/api/testrepository/{repository}",
        f"{JIRA_BASE_URL}/rest/raven/1.0/api/testrepository/{repository}/folders",
    ]

    last_error = None

    for url in urls_to_try:
        r = requests.get(url, headers=headers, auth=auth, verify=VERIFY_SSL)
        print("🔍 Trying:", url, "→", r.status_code)

        if r.status_code == 200:
            return r.json()

        last_error = r.text

    raise Exception(f"❌ Could not list root folders for repository '{repository}'. Last response: {last_error}")