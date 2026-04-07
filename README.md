# 🚀 BRD to Test Case Automation

## 📌 Project Overview
This project automates the generation of test cases from Business Requirement Documents (BRD) using AI.  
It helps QA engineers reduce manual effort and quickly generate structured, high-quality test cases that can be uploaded directly to Jira.

---

## 🎯 Features
- Upload or provide BRD text as input
- Automatically generate test cases in a standard table format:
  - Test Case ID
  - Description
  - Precondition
  - Steps
  - Expected Result
  - Priority
- Export test cases to Excel for Jira bulk upload
- Automatic Test Set assignment during upload
- Simple and intuitive UI for interaction

---

## 🛠️ Tech Stack
- **Frontend:** React
- **Backend:** Python (FastAPI, Uvicorn)
- **AI Model:** Ollama / LLM
- **Test Management:** Jira integration via bulk upload Manual .

---

## 📂 Project Structure
BRD_Automation/
│── backend/
│ ├── api.py
│ ├── scripts/
│ └── utils/
│── frontend/
│ ├── src/
│── output/
│── README.md

---

## ▶️ How to Run

### 1️⃣ Backend
Start the backend server:
```bash
uvicorn api:app --reload --reload-dir scripts
2️⃣ Frontend
cd frontend
npm install
npm start
🔄 Workflow
Provide BRD Text
Input your BRD text into the frontend or via API.
Generate Test Cases
Test cases are automatically generated in a structured table format.
Refinement Block
Review generated test cases.
Provide comments to refine them, e.g.:
"Add edge cases for invalid input"
"Split this into multiple steps"
"Update preconditions with environment setup"
The system updates the table according to your instructions.
Export in CSV , JIRa format & Upload to Jira
Upload using Jira bulk upload - Manual .
The system automatically adds a Test Set column to the Excel file, linking test cases to the correct Test Set in Jira.
📊 Benefits
Eliminates manual test case creation in Jira
Test Set assignment is automated
Reduces QA effort significantly
Works with any BRD (sample or internal)
Interactive refinement ensures high-quality test cases

🧠 Future Enhancements

Support for multi-language BRDs

Advanced AI validations for edge cases
🤝 Contribution

Feel free to fork the repo, suggest improvements, or contribute directly.

🌟 Demo
Input: Sample BRD (e.g., User Registration System)
Output: Fully structured and refined test cases ready for Jira bulk upload
Demonstrates AI-assisted QA workflow
