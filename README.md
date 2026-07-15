# Thesis De-AI Tool / 论文降AI率工具

> 📝 Two-stage LLM pipeline to reduce AI detection scores in academic papers.  
> 📝 基于大语言模型的两阶段管道，降低学术论文的 AI 检测率。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

---

## 📖 目录

- [这是什么？](#这是什么)
- [前置准备](#前置准备)
- [使用步骤](#使用步骤)
- [工作原理](#工作原理)
- [配置说明](#配置说明)
- [常见问题](#常见问题)
- [项目结构](#项目结构)

---

## 这是什么？

写论文时，查重系统除了检测抄袭，还会给每个段落打 **AI 生成概率**。很多学校要求 AI 率低于某个阈值，否则需要返工。

这个工具做的事：

1. 读取你的论文 + 查重报告（带颜色标注的 `.docx`）
2. 自动找出红标（高 AI 率）的段落
3. 通过 DeepSeek 分两阶段改写：
   - **阶段一**：打破 AI 句式（长短句交错、去套话）
   - **阶段二**：升级口语词汇为学术用语
4. 输出一份新的 `.docx`，格式不变

> ⚠️ 仅用于学术辅助，请遵守所在学校的学术规范。

---

## 前置准备

### 1. 安装 Python

需要 **Python 3.8 或更高版本**。  
下载地址：https://www.python.org/downloads/

安装时记得勾选 ✅ **Add Python to PATH**。

验证安装：

```bash
python --version
# 应输出类似：Python 3.12.x
```

### 2. 获取 DeepSeek API Key

> 为什么用 DeepSeek？中文改写质量好、价格便宜（约 ¥1/百万 token）。

**步骤：**

1. 打开 https://platform.deepseek.com/
2. 注册 / 登录（支持微信扫码）
3. 点击左侧菜单 **API Keys**
4. 点击 **创建 API Key**，复制保存

![DeepSeek 控制台示意](https://cdn.deepseek.com/platform-docs/api_keys.png)

首次注册通常会送 **500 万 token 免费额度**，够跑几十篇论文。

### 3. 获取带颜色标注的查重报告

你需要一份 **标红版查重报告**（`.docx` 格式），用于识别哪些段落 AI 率高。

支持以下来源：

| 来源 | 获取方式 |
|------|----------|
| 学校系统 | 下载查重结果的 Word 版 |
| 知网 | 查重后导出标红版 |
| PaperPass | 下载检测报告 |
| 维普 | 下载详细报告 |
| 其他平台 | 只要导出的 docx 中标注段落有红/橙色即可 |

> 💡 文件名建议包含「标红」「查重」「检测」「AIGC」等关键词，脚本能自动识别。

---

## 使用步骤

### 第一步：下载项目

```bash
git clone https://github.com/SAN-399/deai-paper.git
cd deai-paper
```

或者直接下载 ZIP 解压。

### 第二步：放入文件

把以下两个文件放到 `deai-paper` 文件夹里：

```
deai-paper/
├── 我的论文.docx        ← 你的论文（任意名称）
├── 查重报告_标红.docx    ← 标红版查重报告
└── deai_paper.py        ← 脚本本身
```

### 第三步：设置 API Key

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

> 💡 也可以直接双击 `deai_paper.py` 运行，但需要先在系统环境变量里设置 `DEEPSEEK_API_KEY`。

### 第四步：等待完成

运行后会显示进度：

```
==================================================
  论文降AI率脚本
  Stage1: 打破AI句式 -> Stage2: 词汇学术化
==================================================

论文: 我的论文.docx
报告: 查重报告_标红.docx

[1/4] 解析文件中...
      报告: 185段, 平均AI率: 23.5%
      论文: 200段

[2/4] 匹配段落...
      需改写: 45段
      预估费用: CNY 0.04

[3/4] Stage1 打破AI句式 (约需90秒)...
  (1/45) 段12 AI率85% ... OK
  (2/45) 段18 AI率72% ... OK
  ...

[4/4] Stage2 词汇升级 (8段)...

[保存] 我的论文_deai.docx

==================================================
  处理完成!
==================================================
```

### 第五步：检查结果

打开生成的 `你的论文_deai.docx`，检查改写效果。如需微调，可以：

- 把 `deai_paper.py` 中的 `threshold=0.15` 调低（改写更多）或调高（改写更少）
- 调整 `temperature` 参数（0.8~1.0 更灵活，0.2~0.5 更保守）

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

1. **解析** — 从标红报告中提取每个段落的颜色，红色 = 高 AI 率，橙色 = 中 AI 率
2. **匹配** — 将报告段落与原始论文段落对齐
3. **阶段一** — 高温调用 LLM（temp=0.95），打破句式结构
4. **阶段二** — 低温调用 LLM（temp=0.30），仅替换口语词为学术词
5. **保存** — 重建 docx 文件，保留原始格式

---

## 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DEEPSEEK_API_KEY` | 必填 | DeepSeek API 密钥 |
| 阶段一温度 | 0.95 | 越高改写越灵活，越低越保守 |
| 阶段二温度 | 0.30 | 越低越稳定，仅替换词汇 |
| AI 阈值 | 0.15 | AI 率超过此值才会被改写 |
| 跳过段落 | < 25 字 | 太短的段落不处理 |
| 跳过声明 | 自动 | 学位声明、表格描述等自动跳过 |

### 换成 OpenAI

如果不用 DeepSeek，修改 `deai_paper.py` 中的 `call_llm()` 函数：

```python
# 把这行：
"https://api.deepseek.com/v1/chat/completions",
# 改成：
"https://api.openai.com/v1/chat/completions",
```

然后设置 `OPENAI_API_KEY` 环境变量即可。

---

## 常见问题

### Q: 为什么不用第三方库？

为了零门槛——只要装了 Python 就能跑，不需要 `pip install` 任何东西。只用标准库处理 docx 的 ZIP/XML 结构。

### Q: 费用大概多少？

DeepSeek 的 `deepseek-chat` 模型：
- 输入 ¥1/百万 token，输出 ¥2/百万 token
- 每段约 800 token → **每段约 ¥0.0024**
- 一篇论文 50 段需改写 → **约 ¥0.12**

### Q: 脚本如何识别哪些段落需要改？

读取查重报告的 `.docx` 内部 XML，找出红色（`#FF0000` 等）和橙色标注的 run，计算每段的 AI 字符占比。

### Q: 会自动跳过哪些段落？

- 学位论文声明页
- 版权授权声明
- 表格标题和描述
- 少于 25 字符的短段落
- 括号/逗号占比超过 25% 的段落

### Q: 改写效果不理想怎么办？

1. 调整阶段一的 temperature（当前 0.95，试试 0.85 或 1.0）
2. 修改 `SYSTEM_PROMPT_STAGE1` 提示词以适应你的学科风格
3. 检查阶段二是否过度替换：注释掉阶段二的调用

### Q: 报告和论文章节数不一致？

脚本会自动处理。如果数量一致则逐段对应，不一致则按比例映射。

---

## 项目结构

```
deai-paper/
├── deai_paper.py      # 主脚本（零依赖）
├── .gitignore          # 忽略 docx / __pycache__ / .env
├── LICENSE             # MIT 许可证
└── README.md           # 本文件
```

---

## License

MIT — 详见 [LICENSE](LICENSE)。

---

Built with ❤️ for thesis writers everywhere.  
Powered by [DeepSeek API](https://platform.deepseek.com/).
