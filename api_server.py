from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # Allow requests from React frontend

# Load summarized issues once at startup
with open("../data/summarized_issues.json", "r", encoding="utf-8") as f:
    summarized_issues = json.load(f)

@app.route("/")
def home():
    return "✅ Jira Summarizer API is running!"

@app.route("/issues", methods=["GET"])
def get_all_issues():
    return jsonify(summarized_issues)

@app.route("/issues/<string:issue_key>", methods=["GET"])
def get_issue_by_key(issue_key):
    matching = [issue for issue in summarized_issues if issue["key"].lower() == issue_key.lower()]
    if matching:
        return jsonify(matching[0])
    else:
        return jsonify({"error": "❌ No matching issues found."}), 404

@app.route('/api/download-report', methods=['GET'])
def download_report():
    report_path = "../reports/weekly_report.xlsx"
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return jsonify({"error": "Report not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
