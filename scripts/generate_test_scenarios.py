import ollama
import pandas as pd
import os
import csv

# -------- Folders --------
BRD_FOLDER = "/Users/automationtesting/BRD-Test-Automation/BRD_files"
OUTPUT_FOLDER = "/Users/automationtesting/BRD-Test-Automation/output"
MODEL = "minimax-m2.5:cloud"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------- Function to call Ollama --------
def call_ollama(brd_text):
    # Ask AI to generate feature name and test table
    prompt = f"""
You are a QA test scenario generator.

You are a QA test scenario generator.
1. Suggest a short, unique feature name for this BRD.
Return it in EXACT format: Feature Name: <feature_name>
2. Generate test case table as before
Return ONLY table rows using | as delimiter.

BRD:
{brd_text}

Return:
- Feature Name: <name>
- Table rows ONLY using | as delimiter
"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# -------- Loop over all BRD files --------
for filename in os.listdir(BRD_FOLDER):
    if filename.endswith(".txt"):
        brd_path = os.path.join(BRD_FOLDER, filename)
        with open(brd_path, "r") as f:
            brd_text = f.read()

        response = call_ollama(brd_text)

        # ---- Extract Feature Name ----
        lines = response.split("\n")
        feature_name = "Unknown_Feature"
        table_lines = []
        for line in lines:
            if line.lower().startswith("feature name"):
                feature_name = line.split(":")[1].strip().replace(" ", "_")
            elif "|" in line and "Test Case" not in line and "---" not in line:
                table_lines.append(line.strip())

        print(f"🧠 Feature Name: {feature_name}")

        # ---- Create folder for this feature ----
        feature_folder = os.path.join(OUTPUT_FOLDER, feature_name)
        os.makedirs(feature_folder, exist_ok=True)

        # ---- Save raw text ----
        raw_file = os.path.join(feature_folder, filename.replace(".txt", "_raw.txt"))
        with open(raw_file, "w") as f:
            f.write(response)

        # ---- Parse table ----
        rows = []
        for line in table_lines:
            cols = [c.strip().replace("\n", "; ") for c in line.split("|") if c.strip()]
            if len(cols) == 6:
                rows.append(cols)

        if rows:
            df = pd.DataFrame(rows, columns=[
                "Test Case ID", "Description", "Precondition",
                "Steps", "Expected Result", "Priority"
            ])

            # ---- Save Excel ----
            excel_file = os.path.join(feature_folder, filename.replace(".txt", "_test_scenarios.xlsx"))
            df.to_excel(excel_file, index=False)

            # ---- Save CSV for Jira Xray ----
            csv_file = os.path.join(feature_folder, filename.replace(".txt", "_test_scenarios.csv"))
            df.to_csv(csv_file, index=False, quoting=csv.QUOTE_ALL)

            print(f"✅ Generated Excel: {excel_file}")
            print(f"✅ Generated CSV: {csv_file}")
        else:
            print(f"⚠️ No valid table detected for {filename}")