import json
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference

print("📄 Loading summarized issues for Excel report...")
try:
    with open("../data/summarized_issues.json", "r", encoding="utf-8") as f:
        issues = json.load(f)
except FileNotFoundError:
    print("❌ summarized_issues.json file not found. Run summarizer.py first.")
    exit(1)

if not issues:
    print("⚠️ No issues found in summarized_issues.json")
    exit(1)

rows = []
for issue in issues:
    rows.append({
        "Issue ID": issue.get("id", ""),
        "Key": issue.get("key", ""),
        "Summary": issue.get("summary", ""),
        "Description": issue.get("description", ""),
        "AI Summary": issue.get("ai_summary", ""),
        "Extractive Summary": issue.get("extractive_summary", ""),
        "Created Date": issue.get("created", ""),
        "Model Used": issue.get("model_used", ""),
        "Summary Length": issue.get("summary_length", 0),
        "Time Taken (sec)": issue.get("time_taken_sec", 0),
        "Memory Used (MB)": issue.get("memory_used_mb", 0)
    })

df = pd.DataFrame(rows)

# Step 1: Convert 'Created Date' to datetime and remove timezone
df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce").dt.tz_localize(None)

# Step 2: Extract date only and week number for trend analysis
df["Date Only"] = df["Created Date"].dt.date
df["Week"] = df["Created Date"].dt.isocalendar().week

# Step 3: Weekly trend counts
week_counts = df.groupby("Week").size().reset_index(name="Issues Resolved")

# Step 4: Model usage counts for bar chart
model_counts = df["Model Used"].value_counts().reset_index()
model_counts.columns = ["Model", "Usage Count"]

# Step 5: Save report
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = "../reports"
os.makedirs(output_dir, exist_ok=True)

report_filename = os.path.join(output_dir, f"weekly_report_{timestamp}.xlsx")
static_path = os.path.join(output_dir, "weekly_report.xlsx")

with pd.ExcelWriter(report_filename, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name="All Issues", index=False)
    week_counts.to_excel(writer, sheet_name="Weekly Trend", index=False)
    model_counts.to_excel(writer, sheet_name="Model Usage", index=False)

    workbook = writer.book

    # 📈 Line chart for weekly trend
    trend_sheet = writer.sheets["Weekly Trend"]
    line_chart = LineChart()
    line_chart.title = "📈 Weekly Issues Trend"
    line_chart.x_axis.title = "Week Number"
    line_chart.y_axis.title = "Number of Issues"
    data = Reference(trend_sheet, min_col=2, min_row=1, max_row=len(week_counts) + 1)
    categories = Reference(trend_sheet, min_col=1, min_row=2, max_row=len(week_counts) + 1)
    line_chart.add_data(data, titles_from_data=True)
    line_chart.set_categories(categories)
    trend_sheet.add_chart(line_chart, "E2")

    # 📊 Bar chart for model usage
    usage_sheet = writer.sheets["Model Usage"]
    bar_chart = LineChart()
    bar_chart.title = "🤖 Model Usage Count"
    bar_chart.x_axis.title = "Model"
    bar_chart.y_axis.title = "Usage Count"
    bar_data = Reference(usage_sheet, min_col=2, min_row=1, max_row=len(model_counts) + 1)
    bar_categories = Reference(usage_sheet, min_col=1, min_row=2, max_row=len(model_counts) + 1)
    bar_chart.add_data(bar_data, titles_from_data=True)
    bar_chart.set_categories(bar_categories)
    usage_sheet.add_chart(bar_chart, "D2")

print(f"✅ Excel report generated: {report_filename}")
df.to_excel(static_path, index=False)
print(f"📄 Static copy saved: {static_path}")
print("📈 Line chart and 📊 bar chart added to Excel report.")
