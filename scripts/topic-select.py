#!/usr/bin/env python3
"""
topic-select: Interactive topic browser for --topic会话管理.

扫描 topic-session 目录，用 fzf 交互式浏览和选择话题。

Usage:
  topic-select               # FZF interactive selection
  topic-select --list        # Plain numbered list
  topic-select <keyword>     # Filter by keyword

Config:
  Environment variable TOPIC_DIR, or default ~/.topic-session/topics
"""
import os
import re
import sys
import json
import subprocess
from pathlib import Path


def get_topic_dir():
    """Get topic directory from env or default."""
    env_dir = os.environ.get("TOPIC_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    default = Path.home() / ".topic-session" / "topics"
    return default


def parse_frontmatter(filepath):
    """Extract YAML frontmatter from a topic markdown file."""
    content = filepath.read_text(encoding="utf-8")
    topic_name = filepath.stem

    meta = {
        'topic': topic_name,
        'domain': '',
        'updated': '',
        'tags': [],
        'summary': '',
        'sessions': '',
    }

    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return meta

    yaml_block = m.group(1)

    # Extract simple key: value fields
    for key in ['topic', 'domain', 'updated', 'sessions', 'status']:
        vm = re.search(rf'^{key}:\s*(.+)$', yaml_block, re.MULTILINE)
        if vm:
            meta[key] = vm.group(1).strip().strip('"').strip("'")

    # Extract summary (multi-line > block)
    sm = re.search(r'summary:\s*>\s*\n((?:\s+.*\n?)*)', yaml_block)
    if sm:
        summary = ' '.join(sm.group(1).strip().split())
        meta['summary'] = summary

    # Extract tags
    tm = re.search(r'tags:\s*\n((?:\s+- .*\n?)*)', yaml_block)
    if tm:
        meta['tags'] = [t.strip() for t in re.findall(r'- (.+)', tm.group(1))]

    # Normalize date display
    if meta['updated'] and len(meta['updated']) == 8 and meta['updated'].isdigit():
        meta['updated'] = f"{meta['updated'][:4]}-{meta['updated'][4:6]}-{meta['updated'][6:8]}"
    elif not meta['updated']:
        # Try to extract from filename
        date_match = re.search(r'-(\d{8})$', topic_name)
        if date_match:
            d = date_match.group(1)
            meta['updated'] = f"{d[:4]}-{d[4:6]}-{d[6:8]}"

    return meta


def get_preview_content(filepath):
    """Get last 2 Q/A entries from a topic file for preview."""
    content = filepath.read_text(encoding="utf-8")
    content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL).strip()
    if not content:
        return "(empty topic)"

    sections = re.split(r'\n## \d{4}-\d{2}-\d{2}\n', content)
    sections = [s.strip() for s in sections if s.strip()]
    if not sections:
        return "(empty topic)"

    last = sections[-1]
    entries = re.split(r'\n### Q:', last)
    entries = [e.strip() for e in entries if e.strip()]
    if not entries:
        return "(no entries)"

    preview_entries = entries[-2:]
    result_parts = []
    for e in preview_entries:
        lines = e.split('\n')
        if len(lines) > 10:
            lines = lines[:10] + ['...']
        result_parts.append('\n'.join(lines))

    return '\n---\n'.join(result_parts)


def fzf_select(topics_with_meta):
    """Use fzf for interactive fuzzy topic selection."""
    data_lines = []
    for i, (fpath, meta) in enumerate(topics_with_meta):
        updated = meta.get('updated', '')
        domain = meta.get('domain', '')
        display = f"{i+1}\t{domain:<12}\t{updated:<12}\t{meta['topic']}"
        data_lines.append(display)

    input_text = "\n".join(data_lines)

    # Build preview data
    preview_data = {}
    for i, (fpath, meta) in enumerate(topics_with_meta):
        preview_data[str(i)] = get_preview_content(fpath)

    preview_json = json.dumps(preview_data, ensure_ascii=False)
    preview_cmd = (
        'python3 -c "'
        'import json,sys; '
        'preview=' + preview_json + '; '
        'idx=str(int(sys.argv[1].split(chr(9))[0])-1); '
        'print(preview.get(idx,\'(no preview)\'))" {}'
    )

    fzf_cmd = [
        'fzf',
        '--height=70%',
        '--layout=reverse',
        '--border',
        '--header=  #  Domain       Updated      Topic',
        '--prompt=topic> ',
        f'--preview={preview_cmd}',
        '--preview-window=right:60%:wrap',
        '--with-nth=4..',
    ]

    result = subprocess.run(
        fzf_cmd,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0 and result.stdout.strip():
        selected = result.stdout.strip()
        parts = selected.split('\t')
        idx = int(parts[0]) - 1
        return idx
    return None


def list_topics_plain(topics, keyword=None):
    """Display plain numbered list."""
    print(f"\n{'#':>3} {'Domain':<12} {'Updated':<12}  Topic")
    print(f"{'─'*3} {'─'*12} {'─'*12}  ─{'─'*40}")
    for i, (fpath, meta) in enumerate(topics):
        if keyword and keyword.lower() not in meta['topic'].lower():
            continue
        updated = meta.get('updated', '')
        domain = meta.get('domain', '')
        print(f"{i+1:>3} {domain:<12} {updated:<12}  {meta['topic']}")
    print(f"\nTotal: {len(topics)} topics")


def main():
    topic_dir = get_topic_dir()

    if not topic_dir.exists():
        print(f"Topic directory not found: {topic_dir}")
        print("Create one with: mkdir -p {topic_dir}")
        sys.exit(1)

    files = sorted(topic_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print("No topics yet.")
        print("Start one in your AI chat with: 你的问题 --topic 话题名")
        sys.exit(0)

    # Parse all topics
    topics = []
    for f in files:
        meta = parse_frontmatter(f)
        topics.append((f, meta))

    # Determine mode
    args = [a for a in sys.argv[1:] if a]

    if not args or args[0] == 'fzf':
        mode = 'fzf'
        keyword = None
    elif args[0] == '--list':
        mode = 'list'
        keyword = args[1] if len(args) > 1 else None
    else:
        mode = 'list'
        keyword = args[0]

    if mode == 'list':
        list_topics_plain(topics, keyword)

    elif mode == 'fzf':
        try:
            subprocess.run(['which', 'fzf'], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print("fzf not found. Install: brew install fzf (macOS) or apt install fzf (Linux)")
            print("Fallback: topic-select --list")
            list_topics_plain(topics)
            sys.exit(1)

        idx = fzf_select(topics)
        if idx is not None:
            fpath, meta = topics[idx]
            tags = ', '.join(meta['tags'][:4])
            print(f"\n✓ Topic: {meta['topic']}")
            if meta.get('domain'):
                print(f"  Domain: {meta['domain']}")
            if tags:
                print(f"  Tags: {tags}")
            if meta.get('summary'):
                print(f"  Summary: {meta['summary']}")
            print(f"\n  Continue in chat →  继续 --topic {meta['topic']}")
            print(f"  View file →         cat '{fpath}'")
        else:
            print("\nNo topic selected.")


if __name__ == "__main__":
    main()
