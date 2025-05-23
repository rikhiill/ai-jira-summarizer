from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import logging
from datetime import datetime


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# Paths
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reports"))
# Removed fixed LATEST_REPORT since we find latest dynamically now

# Endpoint 1: Health check
@app.get("/")
async def root():
    return {"message": "Jira Summarizer API is running."}

# Endpoint 2: Trigger summarization pipeline
@app.post("/run-pipeline")
async def run_pipeline():
    logger.info("Pipeline run triggered.")
    try:
        # Run the pipeline script synchronously
        # Adjust command if python path or script path differs
        subprocess.run(["python", "run_weekly_pipeline.py"], check=True)
        logger.info("Pipeline run completed successfully.")
        return {"status": "Pipeline completed successfully."}
    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline failed: {e}")
        return HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

# Endpoint 3: Download latest Excel report
@app.get("/download-report")
async def download_report():
    if not os.path.exists(REPORTS_DIR):
        raise HTTPException(status_code=404, detail="Reports directory not found.")

    # List all Excel files in reports directory
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".xlsx")]
    if not files:
        raise HTTPException(status_code=404, detail="No report files found.")

    # Find the latest file by modification time
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(REPORTS_DIR, f)))
    latest_file_path = os.path.join(REPORTS_DIR, latest_file)

    return FileResponse(
        latest_file_path,
        filename=latest_file,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Endpoint 4: (Optional) Serve summarized JSON data
@app.get("/summarized-data")
async def get_summarized_data():
    summary_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/summarized_issues.json"))
    if os.path.exists(summary_path):
        import json
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=404, detail="Summarized data not found.")
