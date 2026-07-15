---
name: deai-paper
description: Reduce AI detection scores in academic papers using a two-stage LLM pipeline. Use when the user needs to lower AI detection rates for a thesis or academic paper, has a DOCX paper and a color-coded AI detection report, mentions terms like 降AI, deai, AI detection, AI率, 论文降重, or wants to rewrite flagged paragraphs to evade AI detectors. Also use when the user asks to process or de-AI academic documents.
---

# De-AI Paper

Two-stage pipeline that rewrites academic papers to reduce AI detection scores.

## When to Use

Trigger when the user:
- Has a thesis/paper and wants to lower AI detection rate
- Mentions 降AI, deai, AI率, or AI detection
- Has both a paper DOCX and a color-coded detection report DOCX
- Asks to rewrite flagged text to sound less AI-generated

## What You Need From the User

1. **Paper** (DOCX) - the original thesis/paper
2. **Detection report** (DOCX) - color-coded report with red/orange highlights
3. **DeepSeek API key** - set as DEEPSEEK_API_KEY env var

## How to Use

Run the bundled script directly:

```bash
python scripts/deai_paper.py
```

### Setup Steps

1. Ask the user for their DeepSeek API key if not already set
2. Set the env var: `$env:DEEPSEEK_API_KEY = "sk-..."` (Windows) or `export DEEPSEEK_API_KEY="sk-..."` (macOS/Linux)
3. Confirm both DOCX files are in the same directory as the script
4. Run the script
5. Output will be [paper_name]_deai.docx

### Important Notes

- Zero external dependencies - uses only Python stdlib
- API cost is minimal (~¥0.0024 per paragraph)
- Script automatically skips declarations, table captions, and short paragraphs
- Stage 1 (temp=0.95): breaks AI sentence patterns
- Stage 2 (temp=0.30): upgrades casual vocabulary to academic register

### If User Does Not Have Files

Guide them to:
1. Get their paper as DOCX
2. Export their school''s plagiarism/AI detection report as DOCX (must have color-coded highlights)
3. Register at https://platform.deepseek.com/ for an API key (free credits on signup)