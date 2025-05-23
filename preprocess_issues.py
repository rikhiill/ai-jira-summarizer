import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer

# Set nltk data path
nltk.data.path.append("C:/Users/pasul/ai-jira-summarizer/backend/nltk_data")

# Initialize tokenizer and stopwords
tokenizer = TreebankWordTokenizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = tokenizer.tokenize(text)
    words = [w for w in words if w not in stop_words]
    return ' '.join(words)

# Extract plain text from Jira's structured "description" field
def extract_description_text(desc_field):
    if not isinstance(desc_field, dict):
        return ""
    try:
        blocks = desc_field.get("content", [])
        all_text = []
        for block in blocks:
            if block.get("type") == "paragraph":
                for sub in block.get("content", []):
                    if sub.get("type") == "text":
                        all_text.append(sub.get("text", ""))
        return " ".join(all_text)
    except Exception as e:
        return ""

# Load raw Jira issues
with open("../data/raw_issues.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

cleaned_issues = []

for issue in raw_data.get("issues", []):
    issue_id = issue.get("id", "")
    issue_key = issue.get("key", "")
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    description = fields.get("description", "")
    created_date = fields.get("created", "")

    description_text = extract_description_text(description)
    
    cleaned_summary = clean_text(summary)
    cleaned_description = clean_text(description_text)
    

    cleaned_issues.append({
        "id": issue_id,
        "key": issue_key,
        "cleaned_summary": cleaned_summary,
        "cleaned_description": cleaned_description,
        "created": created_date
    })

# Save the cleaned output
with open("../data/cleaned_issues.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_issues, f, indent=4)

print("✅ Cleaned issues saved to data/cleaned_issues.json")
