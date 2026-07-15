#!/usr/bin/env python3
"""
论文降AI率脚本
==============
自动检测项目文件夹中的论文和标红查重报告，两阶段处理降低AI检测率。

用法:
    1. 把 论文.docx 和 标红报告.docx 放到本脚本所在目录
    2. 设置环境变量: set DEEPSEEK_API_KEY=sk-你的Key
    3. 双击运行，或执行: python 降AI率脚本.py

输出: 论文_deai.docx

原理:
    Stage 1 (temp=0.95): 打破AI句式结构 → 降低AI检测率
    Stage 2 (temp=0.30): 词汇升级为学术级 → 保持论文正式感

依赖: Python 3.8+ (无需安装第三方包)
"""

import json, os, re, sys, urllib.request, urllib.error
import zipfile, shutil
from pathlib import Path
from xml.etree import ElementTree as ET

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
RED = {"F12828", "FF0000", "FF00000", "C00000", "E60000"}
ORANGE = {"F39800", "FF6600", "FF8C00", "FFA500", "FF7F00"}

# ═══════════════════════════════════════════════════════
# Prompts
# ═══════════════════════════════════════════════════════
P1 = """你是论文编辑，任务是改写文本使其不被AI检测器识别为AI生成。

【核心做法】
1. 每个句子长度都不同。长句(20-30字)后紧跟短句(5-10字)。打破均匀节奏。
2. 三段式排比拆成两项或四项。
3. 删除所有AI套话: "此外""值得注意的是""具有重要意义""发挥着重要作用"
   "在…背景下""从而""有助于""旨在""聚焦于""深远影响""不可或缺"
4. 删除段落结尾的宣告式总结: "提供了参考""奠定了基础""具有…意义"
5. 保留引用标记[1][7]、专业术语、数据、人名
6. 不必太正式，自然就好。

直接输出改写后的文本。"""

P2 = """你是词汇替换工具。下面是已经降过AI检测率的文本，句式结构很好，但部分词汇太口语化。

【任务】只做以下词汇的替换，其他什么都不改：
- "搭" -> "构建"
- "搞" -> "开展"
- "跑" -> "运行"
- "靠" -> "依据"
- "推东西" -> "生成推荐"/"推荐内容"
- "打了个样" -> "提供了参考案例"
- "能(做某事)" -> "能够" (但"功能""智能""性能""可能"不变！)
- "用(某技术)" -> "采用" (但"使用""应用""利用"不变！)
- "老办法" -> "传统方法"
- "跟不上" -> "难以满足"
- "东西" -> "内容"/"数据"
- "聊" -> "讨论"
- "翻了翻" -> "梳理了"
- "门槛低" -> "使用门槛较低"
- "有东西可推" -> "有内容可推荐"
- "找到一条路" -> "提供了路径"

【严禁】不要改写句子结构、不改变段落长度、不加AI套话、不加解释。
直接输出词汇替换后的文本。"""

# ═══════════════════════════════════════════════════════
# 文件自动发现
# ═══════════════════════════════════════════════════════

def find_files():
    """自动发现目录下的论文和检测报告"""
    script_dir = Path(__file__).parent
    docx_files = list(script_dir.glob("*.docx"))

    paper = None
    report = None

    for f in docx_files:
        name = f.name.lower()
        if any(k in name for k in ["标红", "查重", "检测", "aigc", "报告"]):
            report = str(f)
        elif any(k in name for k in ["deai", "降ai", "_v", "_academic"]):
            continue  # 跳过已处理的输出文件
        else:
            if paper is None:
                paper = str(f)

    if not paper:
        # 取最大的docx作为论文
        regular = [f for f in docx_files
                   if not any(k in f.name.lower() for k in ["标红","查重","检测","deai","降ai","_v","_academic"])]
        if regular:
            paper = str(max(regular, key=lambda f: f.stat().st_size))

    return paper, report

# ═══════════════════════════════════════════════════════
# DOCX 读写
# ═══════════════════════════════════════════════════════

SKIP_PATTERNS = [
    r"本人郑重声明", r"本学位论文作者完全了解",
    r"原创性声明", r"版权使用授权",
    r"^\d+\.\s*\S+表\s*\(.*编号.*\)$",
    r"实体属性图如图", r"各实体之间通过外键",
]

def _should_skip(text):
    if len(text) < 25: return True
    if sum(1 for c in text if c in '()（）,，、') > len(text) * 0.25: return True
    for pat in SKIP_PATTERNS:
        if re.search(pat, text): return True
    return False

def parse_colored(filepath):
    with zipfile.ZipFile(filepath, "r") as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    for p_idx, p_elem in enumerate(root.iter(f"{{{NS}}}p")):
        red_text, orange_text, total_text = [], [], []
        for r_elem in p_elem.iter(f"{{{NS}}}r"):
            rpr = r_elem.find(f"{{{NS}}}rPr")
            color = "000000"
            if rpr is not None:
                c = rpr.find(f"{{{NS}}}color")
                if c is not None:
                    color = (c.get(f"{{{NS}}}val") or "000000").upper().lstrip("#")
            t_elem = r_elem.find(f"{{{NS}}}t")
            text = (t_elem.text or "") if t_elem is not None else ""
            total_text.append(text)
            if color in RED: red_text.append(text)
            elif color in ORANGE: orange_text.append(text)
        full_text = "".join(total_text).strip()
        if not full_text or len(full_text) < 10: continue
        ai_chars = sum(len(t) for t in red_text + orange_text)
        tc = len(full_text)
        paras.append({
            "index": p_idx, "xml_index": p_idx, "text": full_text,
            "ai_ratio": ai_chars / tc if tc > 0 else 0,
        })
    return paras

def parse_clean(filepath):
    with zipfile.ZipFile(filepath, "r") as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    for p_idx, p_elem in enumerate(root.iter(f"{{{NS}}}p")):
        texts = [t.text or "" for t in p_elem.iter(f"{{{NS}}}t")]
        full_text = "".join(texts).strip()
        if full_text and len(full_text) >= 10:
            paras.append({"index": p_idx, "xml_index": p_idx, "text": full_text})
    return paras

def match(report_paras, paper_paras, threshold=0.15):
    result = [{"index": pp["index"], "xml_index": pp["xml_index"],
               "text": pp["text"], "ai_ratio": 0.0, "needs_rewrite": False}
              for pp in paper_paras]
    if len(report_paras) == len(paper_paras):
        for i, rp in enumerate(report_paras):
            if i < len(result):
                result[i]["ai_ratio"] = rp["ai_ratio"]
                result[i]["needs_rewrite"] = (rp["ai_ratio"] >= threshold
                                              and not _should_skip(paper_paras[i]["text"]))
    else:
        ratio = len(report_paras) / len(result) if len(result) > 0 else 1
        for i, pp in enumerate(result):
            mi = min(int(i * ratio), len(report_paras) - 1)
            pp["ai_ratio"] = report_paras[mi]["ai_ratio"]
            pp["needs_rewrite"] = (pp["ai_ratio"] >= threshold
                                   and not _should_skip(pp["text"]))
    return result

def save_docx(original_path, output_path, paragraphs):
    shutil.copy2(original_path, output_path)
    with zipfile.ZipFile(output_path, "r") as z:
        doc_xml = z.read("word/document.xml")
        all_files = {name: z.read(name) for name in z.namelist()
                     if name != "word/document.xml"}
    ET.register_namespace("", NS)
    root = ET.fromstring(doc_xml)
    all_p = list(root.iter(f"{{{NS}}}p"))
    rmap = {pp["xml_index"]: pp.get("rewritten_text", pp["text"])
            for pp in paragraphs if pp.get("needs_rewrite")}

    for p_idx, p_elem in enumerate(all_p):
        if p_idx in rmap:
            runs = list(p_elem.iter(f"{{{NS}}}r"))
            if runs:
                for r in runs:
                    for t in r.iter(f"{{{NS}}}t"): t.text = ""
                ft = runs[0].find(f"{{{NS}}}t")
                if ft is not None:
                    ft.text = rmap[p_idx]
                    ft.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    new_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(output_path + ".tmp", "w", zipfile.ZIP_DEFLATED) as zout:
        zout.writestr("word/document.xml", new_xml)
        for name, data in all_files.items():
            zout.writestr(name, data)
    os.replace(output_path + ".tmp", output_path)

# ═══════════════════════════════════════════════════════
# LLM 调用
# ═══════════════════════════════════════════════════════

def call_llm(api_key, system_prompt, user_text, temperature=0.8):
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": 4096,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API HTTP {e.code}: {body[:300]}")
    except Exception as e:
        raise RuntimeError(f"API异常: {e}")

# ═══════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════

def main():
    print("\n" + "=" * 50, flush=True)
    print("  论文降AI率脚本", flush=True)
    print("  Stage1: 打破AI句式 → Stage2: 词汇学术化", flush=True)
    print("=" * 50 + "\n", flush=True)

    # 获取API Key
    api_key = (os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
               or "sk-f6af7c590c004a989e5d7a4db3005e99")  # 默认Key，可替换为你的
    if not api_key:
        print("[错误] 请先设置环境变量:", flush=True)
        print("  PowerShell: $env:DEEPSEEK_API_KEY=\"sk-你的Key\"", flush=True)
        print("  CMD:       set DEEPSEEK_API_KEY=sk-你的Key", flush=True)
        input("\n按回车退出...")
        sys.exit(1)

    # 自动发现文件
    paper, report = find_files()
    if not paper:
        print("[错误] 未找到论文文件(.docx)", flush=True)
        print("请把论文和标红报告放到本脚本所在目录", flush=True)
        input("\n按回车退出...")
        sys.exit(1)
    if not report:
        print("[错误] 未找到检测报告(文件名需含'标红'/'查重'/'检测')", flush=True)
        print("请把标红版查重报告放到本脚本所在目录", flush=True)
        input("\n按回车退出...")
        sys.exit(1)

    print(f"论文: {Path(paper).name}", flush=True)
    print(f"报告: {Path(report).name}\n", flush=True)

    # 解析
    print("[1/4] 解析文件中...", flush=True)
    report_paras = parse_colored(report)
    paper_paras = parse_clean(paper)
    avg_ai = sum(p["ai_ratio"] for p in report_paras) / len(report_paras) if report_paras else 0
    print(f"      报告: {len(report_paras)}段, 平均AI率: {avg_ai:.1%}", flush=True)
    print(f"      论文: {len(paper_paras)}段", flush=True)

    # 匹配
    print("[2/4] 匹配段落...", flush=True)
    paragraphs = match(report_paras, paper_paras)
    to_rewrite = [p for p in paragraphs if p["needs_rewrite"]]
    print(f"      需改写: {len(to_rewrite)}段", flush=True)
    print(f"      预估费用: CNY {len(to_rewrite)*800/1e6*1.0:.2f}", flush=True)

    # Stage 1
    print(f"\n[3/4] Stage1 打破AI句式 (逐段调用API, 约需{len(to_rewrite)*2}秒)...", flush=True)
    done = 0
    for i, pp in enumerate(to_rewrite):
        print(f"  ({i+1}/{len(to_rewrite)}) 段{pp['index']+1} AI率{pp['ai_ratio']:.0%} ...", end=" ", flush=True)
        try:
            pp["rewritten_text"] = call_llm(api_key, P1, pp["text"], 0.95)
            done += 1
            print("OK", flush=True)
        except Exception as e:
            print(f"失败: {e}", flush=True)
            pp["rewritten_text"] = pp["text"]
    print(f"      Stage1完成: {done}/{len(to_rewrite)}", flush=True)

    # Stage 2
    markers = ["搭", "搞", "推东西", "老办法", "打个样", "有东西",
               "聊了", "翻了翻", "串起来", "跑得稳", "跟不上", "省事", "铺好了路"]
    vocab_paras = [p for p in paragraphs
                   if p.get("rewritten_text") and
                   any(m in p["rewritten_text"] for m in markers)]

    if vocab_paras:
        print(f"\n[4/4] Stage2 词汇升级 ({len(vocab_paras)}段)...", flush=True)
        done = 0
        for i, pp in enumerate(vocab_paras):
            print(f"  ({i+1}/{len(vocab_paras)}) 段{pp['index']+1} ...", end=" ", flush=True)
            try:
                new_text = call_llm(api_key, P2, pp["rewritten_text"], 0.3)
                if new_text and len(new_text) > 20:
                    pp["rewritten_text"] = new_text
                    done += 1
                    print("OK", flush=True)
                else:
                    print("无变化", flush=True)
            except Exception as e:
                print(f"失败: {e}", flush=True)
        print(f"      Stage2升级: {done}/{len(vocab_paras)}", flush=True)
    else:
        print(f"\n[4/4] Stage2 无需词汇升级", flush=True)

    # 输出
    for pp in paragraphs:
        if "rewritten_text" not in pp:
            pp["rewritten_text"] = pp["text"]

    output = str(Path(paper).parent / (Path(paper).stem + "_deai.docx"))
    print(f"\n[保存] {Path(output).name}", flush=True)
    save_docx(paper, output, paragraphs)

    print("\n" + "=" * 50, flush=True)
    print("  处理完成!", flush=True)
    print(f"  输出: {Path(output).name}", flush=True)
    print("=" * 50 + "\n", flush=True)
    try:
        input("按回车退出...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[崩溃] {e}", flush=True)
        import traceback
        traceback.print_exc()
        try:
            input("\n按回车退出...")
        except (EOFError, KeyboardInterrupt):
            pass

