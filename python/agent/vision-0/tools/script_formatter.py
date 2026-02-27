#!/usr/bin/env python3
"""
script_formatter.py — Fountain 格式剧本辅助工具

功能：
  1. validate  — 检查 .fountain 文件格式是否合规
  2. to_html   — 将 .fountain 转为可预览的 HTML
  3. stats     — 统计剧本信息（场景数、对话行数、预估时长）
  4. extract   — 提取所有场景标题或角色名（方便导演 Agent 使用）

用法：
  python tools/script_formatter.py validate outputs/02_script/final_script.fountain
  python tools/script_formatter.py stats    outputs/02_script/final_script.fountain
  python tools/script_formatter.py to_html  outputs/02_script/final_script.fountain
  python tools/script_formatter.py extract  scenes outputs/02_script/final_script.fountain
  python tools/script_formatter.py extract  chars  outputs/02_script/final_script.fountain
"""

import sys
import re
from pathlib import Path


# ─── Fountain 解析 ────────────────────────────────────────────────────────────

def parse_fountain(text: str) -> list[dict]:
    """将 Fountain 文本解析为 token 列表。"""
    tokens = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 场景标题：INT. / EXT. 开头，或全大写含空格
        if re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', stripped, re.IGNORECASE):
            tokens.append({'type': 'scene_heading', 'text': stripped})

        # 过渡：> ... < 或 CUT TO: / FADE OUT 等
        elif re.match(r'^>{1}(.+)<{1}$', stripped) or re.match(
            r'^(FADE (IN|OUT|TO)|CUT TO|DISSOLVE TO|SMASH TO):?$', stripped
        ):
            tokens.append({'type': 'transition', 'text': stripped})

        # 角色名：全大写，不含小写字母（且后面跟对话）
        elif stripped and stripped == stripped.upper() and re.match(r'^[A-Z\u4e00-\u9fff][^a-z]+$', stripped):
            tokens.append({'type': 'character', 'text': stripped})

        # 括注（角色名下的情绪说明）
        elif re.match(r'^\(.+\)$', stripped):
            tokens.append({'type': 'parenthetical', 'text': stripped})

        # 空行
        elif stripped == '':
            tokens.append({'type': 'empty', 'text': ''})

        # 动作描述（其余所有非空行）
        else:
            tokens.append({'type': 'action', 'text': stripped})

        i += 1
    return tokens


# ─── 功能实现 ─────────────────────────────────────────────────────────────────

def validate(filepath: str):
    """检查 Fountain 文件基本合规性。"""
    text = Path(filepath).read_text(encoding='utf-8')
    tokens = parse_fountain(text)

    issues = []
    scene_count = sum(1 for t in tokens if t['type'] == 'scene_heading')
    char_count = sum(1 for t in tokens if t['type'] == 'character')

    if scene_count == 0:
        issues.append("❌ 未找到任何场景标题（Scene Heading），请确认使用 INT./EXT. 格式")
    if char_count == 0:
        issues.append("❌ 未找到任何角色名，请确认角色名使用全大写")

    # 检查角色名后是否直接跟对话
    for i, tok in enumerate(tokens):
        if tok['type'] == 'character':
            next_non_empty = next(
                (t for t in tokens[i+1:] if t['type'] != 'empty'), None
            )
            if next_non_empty and next_non_empty['type'] not in ('action', 'parenthetical', 'character'):
                pass  # 对话行被归类为 action，暂不细分

    if issues:
        print("\n".join(issues))
    else:
        print(f"✅ 格式验证通过：{scene_count} 个场景，{char_count} 处对话角色名。")


def stats(filepath: str):
    """统计剧本信息并预估时长。"""
    text = Path(filepath).read_text(encoding='utf-8')
    tokens = parse_fountain(text)

    scenes = [t for t in tokens if t['type'] == 'scene_heading']
    chars = [t for t in tokens if t['type'] == 'character']
    actions = [t for t in tokens if t['type'] == 'action']

    # 行业规则：1 页剧本 ≈ 1 分钟，约 55 行/页
    total_lines = len([t for t in tokens if t['type'] != 'empty'])
    estimated_pages = round(total_lines / 55, 1)
    estimated_minutes = estimated_pages  # 1:1

    print("📊 剧本统计")
    print("─" * 30)
    print(f"  场景数（Scenes）   : {len(scenes)}")
    print(f"  对话角色次数        : {len(chars)}")
    print(f"  动作描述行数        : {len(actions)}")
    print(f"  有效行数            : {total_lines}")
    print(f"  预估页数            : {estimated_pages} 页")
    print(f"  预估时长            : {estimated_minutes} 分钟")
    print()
    print("🎬 场景列表：")
    for i, s in enumerate(scenes, 1):
        print(f"  {i:02d}. {s['text']}")


def to_html(filepath: str):
    """将 Fountain 转为 HTML 预览文件。"""
    text = Path(filepath).read_text(encoding='utf-8')
    tokens = parse_fountain(text)
    output_path = Path(filepath).with_suffix('.html')

    html_parts = ["""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>剧本预览</title>
<style>
  body { font-family: "Courier New", Courier, monospace; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f9f6f1; color: #222; }
  .scene-heading { font-weight: bold; margin-top: 2em; text-transform: uppercase; border-top: 1px solid #ccc; padding-top: 0.5em; }
  .character { text-align: center; font-weight: bold; margin-top: 1em; }
  .parenthetical { text-align: center; font-style: italic; color: #555; }
  .action { margin: 0.5em 0; line-height: 1.6; }
  .transition { text-align: right; font-style: italic; margin: 1em 0; }
  .dialogue { margin: 0 10%; line-height: 1.6; }
</style>
</head>
<body>
<h1 style="text-align:center; font-size:1.2em; border-bottom:2px solid #333; padding-bottom:0.5em;">剧本</h1>
"""]

    in_dialogue = False
    for tok in tokens:
        t, text = tok['type'], tok['text']
        if t == 'scene_heading':
            html_parts.append(f'<p class="scene-heading">{text}</p>')
            in_dialogue = False
        elif t == 'character':
            html_parts.append(f'<p class="character">{text}</p>')
            in_dialogue = True
        elif t == 'parenthetical':
            html_parts.append(f'<p class="parenthetical">{text}</p>')
        elif t == 'transition':
            html_parts.append(f'<p class="transition">{text}</p>')
            in_dialogue = False
        elif t == 'action':
            cls = 'dialogue' if in_dialogue else 'action'
            html_parts.append(f'<p class="{cls}">{text}</p>')
            if not in_dialogue:
                in_dialogue = False
        elif t == 'empty':
            in_dialogue = False

    html_parts.append("</body></html>")
    output_path.write_text("\n".join(html_parts), encoding='utf-8')
    print(f"✅ HTML 预览已生成：{output_path}")


def extract(mode: str, filepath: str):
    """提取场景列表或角色列表。"""
    text = Path(filepath).read_text(encoding='utf-8')
    tokens = parse_fountain(text)

    if mode == 'scenes':
        scenes = [t['text'] for t in tokens if t['type'] == 'scene_heading']
        print(f"🎬 共 {len(scenes)} 个场景：")
        for i, s in enumerate(scenes, 1):
            print(f"  {i:02d}. {s}")
    elif mode == 'chars':
        chars = sorted(set(t['text'] for t in tokens if t['type'] == 'character'))
        print(f"👤 共 {len(chars)} 个角色：")
        for c in chars:
            print(f"  - {c}")
    else:
        print(f"❌ 未知模式：{mode}，请使用 'scenes' 或 'chars'")


# ─── CLI 入口 ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == 'validate':
        validate(sys.argv[2])
    elif command == 'stats':
        stats(sys.argv[2])
    elif command == 'to_html':
        to_html(sys.argv[2])
    elif command == 'extract':
        if len(sys.argv) < 4:
            print("用法：extract <scenes|chars> <filepath>")
            sys.exit(1)
        extract(sys.argv[2], sys.argv[3])
    else:
        print(f"❌ 未知命令：{command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
