import json
from datetime import datetime
from collections import defaultdict, Counter
from dateutil import parser
import os

# Load AI summaries
print("📄 Loading summarized issues...")
with open("../data/summarized_issues.json", "r", encoding="utf-8") as f:
    issues = json.load(f)

# Group by week number
weekly_data = defaultdict(list)

for issue in issues:
    created = issue.get("created", "")
    if not created or created.startswith("1970"):
        print(f"⚠️ Skipped issue {issue.get('key', 'N/A')} – missing 'created' date")
        continue
    try:
        dt = parser.parse(created)
        year_week = f"{dt.year}-W{dt.isocalendar().week}"
        issue['summary_length'] = issue.get('summary_length', len(issue.get('ai_summary', '').split()))
        weekly_data[year_week].append(issue)
    except Exception as e:
        print(f"❌ Error parsing date '{created}' for issue {issue.get('key', 'N/A')}: {str(e)}")

print(f"📦 Grouped issues by week: {len(weekly_data)} weeks")

# Prepare weekly summaries
weekly_reports = {}

for week, entries in weekly_data.items():
    summary_lengths = [entry.get('summary_length', 0) for entry in entries]
    keywords = [entry['summary'].split()[0].lower() if entry.get('summary') else "unknown" for entry in entries]
    top_keywords = Counter(keywords).most_common(3)

    report_lines = [
        f"# 📅 Week: {week}",
        f"Total Issues: {len(entries)}",
        f"Average Summary Length: {sum(summary_lengths) // len(summary_lengths)} words",
        "Most Frequent Work Types: " + ", ".join([f"{kw} ({count})" for kw, count in top_keywords]),
        "",
        "## ✨ Highlights"
    ]

    for issue in entries:
        key = issue.get("key", "N/A")
        summary = issue.get("ai_summary", "No summary")
        report_lines.append(f"- [{key}]: {summary}")

    weekly_reports[week] = "\n".join(report_lines)

# Create output directory
output_dir = "../reports"
os.makedirs(output_dir, exist_ok=True)

# Save as individual .txt files
for week, content in weekly_reports.items():
    file_path = os.path.join(output_dir, f"{week}_report.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Saved: {file_path}")
