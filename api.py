from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import os
import shutil
import pandas as pd

# Import your existing functions
from scripts.genearteTestSetTestcases import call_ollama, parse_ai_table, get_feature_name_from_ai , create_test_set

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder to store generated files
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Serve the output folder for static download
app.mount("/output", StaticFiles(directory=OUTPUT_FOLDER), name="output")


@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    """
    Upload BRD file, generate test cases using AI, save CSV/Excel, return preview & download links.
    """
    try:
        file_path = f"temp_{file.filename}"

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read BRD content
        with open(file_path, "r", encoding="utf-8") as f:
            brd_text = f.read()

        # AI processing
        feature_name = get_feature_name_from_ai(brd_text)
        ai_output = call_ollama(brd_text)
        
        testset_key = create_test_set(feature_name)
        
        # Parse AI output to DataFrame
        df = parse_ai_table(ai_output,testset_key)  # testset_key empty for now

        # Save CSV & Excel
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        csv_filename = f"{feature_name}.csv"
        excel_filename = f"{feature_name}.xlsx"
        csv_path = os.path.join(OUTPUT_FOLDER, csv_filename)
        excel_path = os.path.join(OUTPUT_FOLDER, excel_filename)
        df.to_csv(csv_path, index=False)
        df.to_excel(excel_path, index=False)

        # Clean up uploaded file
        file.file.close()
        os.remove(file_path)

        # Return preview & download URLs
        return {
            "feature_name": feature_name,
            "preview": df.to_dict(orient="records"),
            "csv_file": f"output/{csv_filename}",
            "excel_file": f"output/{excel_filename}",
             "testset_key": testset_key
        }

    except Exception as e:
        print("ERROR in /generate:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate test cases: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Endpoint to download CSV or Excel files.
    """
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
    
def get_next_version(feature_name):
    files = os.listdir(OUTPUT_FOLDER)
    versions = []

    for f in files:
        if f.startswith(feature_name) and f.endswith(".csv"):
            if "_v" in f:
                try:
                    v = int(f.split("_v")[-1].split(".")[0])
                    versions.append(v)
                except:
                    pass
            else:
                versions.append(1)

    return max(versions) + 1 if versions else 1


# @app.post("/refine")
# async def refine(prompt: str = Body(...), feature_name: str = Body(...)):
#     try:
#         # Find latest version
#         version = get_next_version(feature_name) - 1
#         base_file = f"{feature_name}.csv" if version == 1 else f"{feature_name}_v{version}.csv"
#         base_path = os.path.join(OUTPUT_FOLDER, base_file)

#         if not os.path.exists(base_path):
#             raise HTTPException(status_code=404, detail="Base test cases not found")

#         df_old = pd.read_csv(base_path)
#         old_text = df_old.to_string(index=False)

#         # Build prompt
#         full_prompt = f"""
#         Existing Test Cases:
#         {old_text}

#         User Instruction:
#         {prompt}

#         Improve and refine test cases. Return table format.
#         """

#         ai_output = call_ollama(full_prompt)

#         new_df = parse_ai_table(ai_output, testset_key="")

#         # New version
#         new_version = version + 1
#         new_csv = os.path.join(OUTPUT_FOLDER, f"{feature_name}_v{new_version}.csv")
#         new_excel = os.path.join(OUTPUT_FOLDER, f"{feature_name}_v{new_version}.xlsx")

#         new_df.to_csv(new_csv, index=False)
#         new_df.to_excel(new_excel, index=False)

#         return {
#             "message": f"Refined to version v{new_version}",
#             "version": new_version,
#             "preview": new_df.to_dict(orient="records"),
#             "csv_file": new_csv,
#             "excel_file": new_excel
#         }

#     except Exception as e:
#         print("ERROR in /refine:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine")
async def refine(prompt: str = Body(...), feature_name: str = Body(...)):
    try:
        base_file = f"{feature_name}.csv"
        base_path = os.path.join(OUTPUT_FOLDER, base_file)

        print("Using file:", base_path)

        if not os.path.exists(base_path):
            raise HTTPException(status_code=404, detail="Base test cases not found")

        # Read existing file
        df_old = pd.read_csv(base_path)
        old_text = df_old.to_string(index=False)

        # Build AI prompt
        full_prompt = f"""
        Existing Test Cases:
        {old_text}

        User Instruction:
        {prompt}

        Improve and refine test cases.
        Keep same structure.
        Return ONLY table rows using | delimiter.
        """

        ai_output = call_ollama(full_prompt)

        # IMPORTANT: keep same testset_key if needed
        new_df = parse_ai_table(ai_output, testset_key="")

        # 🔁 OVERWRITE SAME FILES
        csv_path = os.path.join(OUTPUT_FOLDER, f"{feature_name}.csv")
        excel_path = os.path.join(OUTPUT_FOLDER, f"{feature_name}.xlsx")

        new_df.to_csv(csv_path, index=False)
        new_df.to_excel(excel_path, index=False)

        return {
            "message": "Test cases refined successfully",
            "preview": new_df.to_dict(orient="records"),
            "csv_file": f"output/{feature_name}.csv",
            "excel_file": f"output/{feature_name}.xlsx"
        }

    except Exception as e:
        print("ERROR in /refine:", str(e))
        raise HTTPException(status_code=500, detail=str(e))