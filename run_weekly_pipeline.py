import subprocess
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Path to Python inside virtual environment
venv_python = os.path.join("venv", "Scripts", "python.exe")

logging.info("🚀 Starting Weekly Jira Summary Pipeline...")

try:
    logging.info("🔧 Step 1: Preprocessing Jira issues...")
    subprocess.run([venv_python, "preprocess_issues.py"], check=True)

    logging.info("🧠 Step 2: Generating AI summaries...")
    subprocess.run([venv_python, "summarizer.py"], check=True)

    logging.info("📊 Step 3: Creating weekly Excel report...")
    subprocess.run([venv_python, "report_generator.py"], check=True)

    logging.info("✅ Weekly pipeline completed successfully!")

except subprocess.CalledProcessError as e:
    logging.error(f"❌ Error occurred in the pipeline: {e}")
