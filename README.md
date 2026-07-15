# Thesis De-AI Tool / 论文降AI率工具

> 📝 Two-stage LLM pipeline to reduce AI detection scores in academic papers.  
> 📝 基于大语言模型的两阶段管道，降低学术论文的 AI 检测率。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

---

## ✨ Features / 功能

- **Zero dependencies** — pure Python 3.8+ standard library
- **Smart file detection** — auto-discovers paper and AI-detection report in the same folder
- **Two-stage pipeline**:
  - Stage 1 (high temperature): breaks uniform AI sentence patterns to lower detection scores
  - Stage 2 (low temperature): upgrades casual/slang vocabulary to academic register
- **Color-aware parsing** — reads color-coded paragraphs from detection reports (red = high AI probability, orange = medium)
- **Preserves formatting** — outputs a clean `.docx` with original structure intact

---

## 🚀 Quick Start / 快速开始

### 1. Prerequisites / 环境要求

- Python 3.8 or higher
- A [DeepSeek API key](https://platform.deepseek.com/) (or any OpenAI-compatible endpoint)

### 2. Setup / 配置

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/deai-paper.git
cd deai-paper
```

Set your API key as an environment variable:

```bash
# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="sk-your-key-here"

# macOS / Linux
export DEEPSEEK_API_KEY="sk-your-key-here"
```

### 3. Prepare files / 准备文件

Place two `.docx` files in the project folder:

| File | Description |
|------|-------------|
| `paper.docx` | Your original thesis / paper (any filename works) |
| `report.docx` | AI detection report with color-coded paragraphs (filename should contain keywords like 标红, 查重, 检测, AIGC, or 报告) |

### 4. Run / 运行

```bash
python deai_paper.py
```

Output: `paper_deai.docx` — your de-AI``d paper with lowered detection score.

---

## 🔧 How It Works / 工作原理

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  paper.docx  │────▶│  Parse & Match   │────▶│  Stage 1: Break │
│  report.docx │     │  colored paras   │     │  AI patterns    │
└──────────────┘     └──────────────────┘     │  (temp=0.95)    │
                                              └────────┬────────┘
                                                       │
┌─────────────────┐     ┌──────────────────┐          │
│ paper_deai.docx │◀────│  Rebuild DOCX    │◀─────────┘
└─────────────────┘     └──────────────────┘     ┌─────────────────┐
                                                 │  Stage 2: Vocab │
                                                 │  upgrade        │
                                                 │  (temp=0.30)    │
                                                 └─────────────────┘
```

1. **Parse** — reads the detection report, mapping each paragraph to its AI probability (based on red/orange highlighting)
2. **Match** — aligns report paragraphs with the original paper paragraphs
3. **Stage 1** — rewrites high-AI paragraphs with high-temperature LLM calls to break predictable patterns
4. **Stage 2** — selectively upgrades overly casual vocabulary to academic equivalents
5. **Save** — rebuilds the DOCX with rewritten content, preserving all original formatting

---

## 📋 Configuration / 配置说明

| Setting | Default | Description |
|---------|---------|-------------|
| `DEEPSEEK_API_KEY` | (required) | Your DeepSeek API key |
| `temperature` (Stage 1) | 0.95 | Higher = more creative rewrites |
| `temperature` (Stage 2) | 0.30 | Lower = conservative vocab swaps |
| `ai_threshold` | 0.15 | Minimum AI ratio to trigger rewrite |

### Using OpenAI instead of DeepSeek

Set `OPENAI_API_KEY` and modify the API endpoint in `call_llm()`:

```python
"https://api.openai.com/v1/chat/completions"
```

---

## ⚠️ Important Notes / 注意事项

- **This tool is for educational and research purposes only.** Use responsibly and in accordance with your institution``s academic integrity policies.
- **API costs apply** — each paragraph costs roughly ¥0.0008 (800 tokens). A typical thesis of 200 paragraphs costs ~¥0.16.
- The tool skips sections like declarations, acknowledgments, and table descriptions automatically.
- Output quality depends on the LLM. DeepSeek-V3 is recommended for Chinese academic text.

---

## 📁 Project Structure

```
deai-paper/
├── deai_paper.py      # Main script
├── .gitignore          # Ignore docx, pycache, env files
├── LICENSE             # MIT License
└── README.md           # This file
```

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

## 🙏 Credits

Built with ❤️ for thesis writers everywhere.  
Powered by [DeepSeek API](https://platform.deepseek.com/).
