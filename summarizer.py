import json
from transformers import pipeline
import os
import time
import psutil
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

import nltk
nltk.data.path.append(r"C:\Users\pasul\nltk_data")

# Configurable summary length
MIN_SUMMARY_LENGTH = 10
MAX_SUMMARY_LENGTH = 50

def extractive_summary(text, num_sentences=1):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return ' '.join(str(sentence) for sentence in summary)

print("🔍 Loading cleaned issues...")
with open("../data/cleaned_issues.json", "r", encoding="utf-8") as f:
    issues = json.load(f)

print("🧠 Loading summarization model (DistilBART)...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarized_data = []

for issue in issues:
    issue_id = issue.get("id", "")
    issue_key = issue.get("key", "")
    summary = issue.get("cleaned_summary", "")
    description = issue.get("cleaned_description", "")
    created = issue.get("created", "") or issue.get("created_date", "")

    if not created:
        created = "1970-01-01T00:00:00"
    full_text = (summary + ". " + description).strip()

    print(f"\n📝 Summarizing issue {issue_key}:")
    print(f"   → Input text: '{full_text}'")

    if len(full_text) < 10:
        print("   ⚠️ Skipped (text too short)")
        ai_summary = "No meaningful content"
        extractive = "No meaningful content"
        time_taken = 0
        memory_used = 0
    else:
        try:
            start = time.time()
            result = summarizer(
                full_text,
                max_length=MAX_SUMMARY_LENGTH,
                min_length=MIN_SUMMARY_LENGTH,
                do_sample=False
            )
            ai_summary = result[0]['summary_text']
            end = time.time()

            # Extractive summary
            extractive = extractive_summary(full_text)

            # Performance metrics
            process = psutil.Process(os.getpid())
            memory_used = process.memory_info().rss / 1024 / 1024  # MB
            time_taken = end - start

            print(f"   ✅ AI Summary: {ai_summary}")
            print(f"   🧠 Extractive Summary: {extractive}")
            print(f"   ⏱️ Time taken: {time_taken:.2f}s | 💾 Memory used: {memory_used:.2f}MB")

        except Exception as e:
            ai_summary = f"Summarization failed: {str(e)}"
            extractive = "N/A"
            time_taken = 0
            memory_used = 0
            print(f"   ❌ Error: {ai_summary}")

    summarized_data.append({
        "id": issue_id,
        "key": issue_key,
        "summary": summary,
        "description": description,
        "ai_summary": ai_summary,
        "extractive_summary": extractive,
        "summary_length": len(ai_summary.split()) if ai_summary else 0,
        "created": created,
        "model_used": "DistilBART",
        "time_taken_sec": round(time_taken, 2),
        "memory_used_mb": round(memory_used, 2)
    })

# Save output
with open("../data/summarized_issues.json", "w", encoding="utf-8") as f:
    json.dump(summarized_data, f, indent=4)

print("\n✅ AI summaries saved to ../data/summarized_issues.json")
