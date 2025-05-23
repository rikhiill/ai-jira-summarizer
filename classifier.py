import json

# Load raw data
with open("../data/raw_issues.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

classified_issues = []

# Define basic rule-based classifier
def classify_status(status_name):
    status_name = status_name.lower()
    if status_name in ["done", "closed", "resolved"]:
        return "Completed"
    elif status_name in ["in progress", "review", "in review"]:
        return "In Progress"
    elif status_name in ["to do", "open", "backlog"]:
        return "To Do"
    else:
        return "Unknown"

# Process each issue
for issue in raw_data.get("issues", []):
    issue_id = issue.get("id", "")
    issue_key = issue.get("key", "")
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    
    # Extract status from nested structure
    status_obj = fields.get("status", {})
    status_name = status_obj.get("name", "Unknown")

    classification = classify_status(status_name)

    classified_issues.append({
        "id": issue_id,
        "key": issue_key,
        "summary": summary,
        "jira_status": status_name,
        "classified_status": classification
    })

# Save the classified issues
with open("../data/classified_issues.json", "w", encoding="utf-8") as f:
    json.dump(classified_issues, f, indent=4)

print("✅ Issues classified and saved to data/classified_issues.json")
