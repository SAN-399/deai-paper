# Thesis De-AI Tool / 论文降AI率工具

> 📝 Two-stage LLM pipeline to reduce AI detection scores in academic papers.  
> 📝 基于大语言模型的两阶段管道，降低学术论文的 AI 检测率。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

---

## 📖 目录

- [大白话指南（第一次用必看）](#大白话指南)
- [前置准备](#前置准备)
- [详细使用步骤](#详细使用步骤)
- [工作原理](#工作原理)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 大白话指南

> 给没用过命令行、不懂编程的同学看 👇

### 这个工具是干嘛的？

你写论文时可能用 ChatGPT 或别的 AI 帮忙润色过，结果学校查重系统一检测，说你的论文"AI 生成概率太高"。这就很烦——明明是你自己写的，只是让 AI 改了个表述，就被打回来了。

这个工具帮你把论文"去 AI 味"。它不是简单的同义词替换，而是让句子读起来更像人写的——有长有短、不套模板、不背八股。

### 你需要准备三样东西

**1. 你的论文**（.docx 格式）

就是 Word 文档，你平时写的那个。

**2. 学校的查重报告**（.docx 格式）

学校查重后会给你一份报告，打开能看到哪些段落被标红了。把它下载下来，保存成 Word 格式。

> ⚠️ 必须是带颜色的那种！如果报告里只有"相似度 30%"一个数字，没有逐段标红，那不行。

**3. DeepSeek 的 API Key**

这相当于一个"通行证"，让脚本能调用 AI 帮你改写。获取方法很简单：

- 打开 https://platform.deepseek.com/
- 微信扫码注册（30 秒搞定）
- 点左边「API Keys」→「创建 API Key」
- 复制那一长串 `sk-` 开头的字符

> 💰 别担心费用——注册送 500 万 token，够你用几十次。一篇论文大概花一毛钱。

### 怎么跑起来？

**第一步：安装 Python**

去 https://www.python.org/ 下载，安装时务必勾选「Add Python to PATH」。

验证装好了没：按 `Win+R`，输入 `cmd`，在弹出的黑窗口里敲 `python --version`，显示版本号就 OK。

**第二步：下载脚本**

在本页面点绿色的「Code」按钮 →「Download ZIP」，解压到桌面。

**第三步：把文件放进去**

打开解压出来的 `deai-paper` 文件夹，把你的论文和查重报告拖进去。

**第四步：运行**

回到那个黑窗口（CMD），输入：

```
cd 桌面\deai-paper
set DEEPSEEK_API_KEY=sk-你刚才复制的那个Key
python deai_paper.py
```

然后等着就行。屏幕上会显示进度：处理了多少段、花了多少钱。跑完后文件夹里会多出一个 `xxx_deai.docx`，就是降完 AI 率的论文。

### 如果跑不起来？

大概率是 Python 没装好。重新装一遍，记得勾选那个「Add Python to PATH」就行。

---

## 前置准备

### 1. 安装 Python

需要 **Python 3.8 或更高版本**。  
下载地址：https://www.python.org/downloads/

安装时勾选 ✅ **Add Python to PATH**。验证：

```bash
python --version
```

### 2. 获取 DeepSeek API Key

1. 打开 https://platform.deepseek.com/
2. 注册 / 登录（支持微信扫码）
3. 左侧菜单 → **API Keys** → **创建 API Key**

首次注册送 **500 万 token 免费额度**。

### 3. 获取带颜色标注的查重报告

需要 `.docx` 格式的标红版报告，来源：

| 来源 | 获取方式 |
|------|----------|
| 学校系统 | 下载查重结果 Word 版 |
| 知网 | 导出标红版报告 |
| PaperPass / 维普 | 下载详细报告 |
| 其他平台 | 导出带颜色标注的 docx |

> 💡 文件名含「标红」「查重」「检测」「AIGC」关键词可被自动识别。

---

## 详细使用步骤

### 第一步：下载

```bash
git clone https://github.com/SAN-399/deai-paper.git
cd deai-paper
```

或下载 ZIP 解压。

### 第二步：放文件

```
deai-paper/
├── 你的论文.docx          ← 论文
├── 查重报告_标红.docx      ← 标红报告
└── deai_paper.py          ← 脚本
```

### 第三步：设置 Key 并运行

**Windows（PowerShell）：**
```powershell
$env:DEEPSEEK_API_KEY = "sk-你的密钥"
python deai_paper.py
```

**Windows（CMD）：**
```cmd
set DEEPSEEK_API_KEY=sk-你的密钥
python deai_paper.py
```

**macOS / Linux：**
```bash
export DEEPSEEK_API_KEY="sk-你的密钥"
python deai_paper.py
```

### 第四步：看进度

```
==================================================
  论文降AI率脚本
==================================================

论文: 我的论文.docx
报告: 查重报告_标红.docx

[1/4] 解析文件中...  报告: 185段, 平均AI率: 23.5%
[2/4] 匹配段落...    需改写: 45段, 预估费用: CNY 0.04
[3/4] Stage1 打破AI句式 (约需90秒)...
  (1/45) 段12 AI率85% ... OK
  ...
[4/4] Stage2 词汇升级 (8段)...

[保存] 我的论文_deai.docx
  处理完成!
```

### 第五步：检查

打开 `你的论文_deai.docx`，检查改写效果。微调参数：

- `threshold=0.15` → 调低改写更多，调高改写更少
- `temperature` → 0.8~1.0 更灵活，0.2~0.5 更保守

---

## 工作原理

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

1. **解析** — 从标红报告提取段落颜色，红色=高 AI 率，橙色=中 AI 率
2. **匹配** — 报告段落与论文段落对齐
3. **阶段一** — 高温调用 LLM（temp=0.95），打破句式结构
4. **阶段二** — 低温调用 LLM（temp=0.30），仅替换口语词为学术词
5. **保存** — 重建 docx，保留原始格式

---

## 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DEEPSEEK_API_KEY` | 必填 | DeepSeek API 密钥 |
| 阶段一温度 | 0.95 | 越高越灵活 |
| 阶段二温度 | 0.30 | 越低越稳定 |
| AI 阈值 | 0.15 | 超过此值才改写 |
| 最小段落长度 | 25 字符 | 更短的自动跳过 |

### 换 OpenAI

修改 `deai_paper.py` 中 `call_llm()` 的 URL：

```python
"https://api.openai.com/v1/chat/completions"
```

然后设 `OPENAI_API_KEY` 即可。

---

## 常见问题

**Q: 费用多少？**  
约 ¥0.0024/段。一篇论文 50 段需改写 → 约 ¥0.12。

**Q: 如何识别哪些段落要改？**  
读取报告 docx 的 XML，找红/橙色标注的 run，算每段 AI 字符占比。

**Q: 哪些段落自动跳过？**  
学位声明、版权声明、表格标题、<25 字段落、符号占比 >25% 的段落。

**Q: 效果不好怎么办？**  
调 temperature、改 threshold、或编辑脚本中的提示词。

**Q: 报告和论文章节数不一样？**  
自动按比例映射处理。

**Q: 完全不碰代码能行吗？**  
能。看上面「大白话指南」，一步步来就行。

---

## 项目结构

```
deai-paper/
├── deai_paper.py      # 主脚本（零依赖）
├── .gitignore
├── LICENSE             # MIT
└── README.md
```

---

## License

MIT — 详见 [LICENSE](LICENSE)。

Built with ❤️ for thesis writers everywhere.  
Powered by [DeepSeek API](https://platform.deepseek.com/).
