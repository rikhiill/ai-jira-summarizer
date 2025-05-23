import subprocess
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
print("Backend directory is:", backend_dir)

# Use the current Python executable (which should be from the venv)
python_executable = sys.executable

try:
    print("Running jira_fetcher.py...")
    result = subprocess.run([python_executable, "jira_fetcher.py"], cwd=backend_dir)
    result.check_returncode()
    print("[SUCCESS] Jira issues fetched and saved")

    print("Running summarizer.py...")
    result = subprocess.run([python_executable, "summarizer.py"], cwd=backend_dir)
    result.check_returncode()
    print("[SUCCESS] Summarizer finished")

    print("Running report_generator.py...")
    result = subprocess.run([python_executable, "report_generator.py"], cwd=backend_dir)
    result.check_returncode()
    print("[SUCCESS] Report generated")

except subprocess.CalledProcessError as e:
    print(f"Error in {e.cmd[1]}")  # prints which script failed
