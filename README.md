# Topic Session

**AI conversations have no memory. This fixes that.**

A lightweight conversation management system for AI agents. Mark any message with `--topic topic-name` to save structured records to disk — searchable, reusable across sessions, browsable from the terminal.

Works with any AI agent that respects the `--topic` convention (Hermes Agent, Claude Code, Codex, OpenCode, or a custom wrapper).

---

## The Problem

You're deep in an AI conversation, going back and forth to understand something complex. After 30+ exchanges, you finally have clarity. You ask: *"compile everything we discussed into a formal document."*

The AI produces something. But it's missing things. Key points from the first 10 messages are gone. A nuanced argument you made 5 turns ago is reduced to a vague sentence. Another round of "add this, fix that" — still not right.

This gets **much worse** when you interrupt the main thread to ask unrelated questions. The AI's context window compresses, earlier details get squeezed out, and the final document is a shadow of what you actually discussed.

**The root cause:** AI conversations are ephemeral streams. They have no persistent, structured record of what was discussed. Everything relies on the model's context window — which is finite, compressed, and lossy.

Topic Session fixes this by saving every discussion as structured Q&A to a Markdown file — incrementally, as you talk. When you're ready to compile:

1. The full, un-lossy record exists on disk
2. The AI reads it directly — no context-window compression
3. The generated document is complete, every key point preserved

No more "the AI forgot what we said 10 messages ago."

## How It Works

```
Chat                              Filesystem
────                              ────────
You: analyze these routes         → industry-agent-20260530.md
     --topic industry-agent           ↑ Q: Technical route analysis
                                      ↑ A: Layered hybrid architecture...
You: next session                  → industry-agent-20260601.md
     continue --topic industry-agent  ↑ Q: RAG vs training
(I read history, summarize where      ↑ A: Data flywheel...
 you left off, ask where to go)
```

## Quick Start (30 seconds)

```bash
# 1. Set up
mkdir -p ~/.topic-session/topics

# 2. (Optional) Install the terminal browser
chmod +x install.sh && ./install.sh

# 3. Use it
# In your AI chat:
#   analyze this market --topic market-analysis
#   continue --topic market-analysis
#   --topic --list
```

## Installation

### As a Hermes Agent Skill

```bash
git clone https://github.com/sunquan0405/topic-session.git
cd topic-session
hermes skills install SKILL.md
```

### Standalone (any AI agent)

Copy the script to your PATH:

```bash
cp scripts/topic-select.py ~/bin/topics
chmod +x ~/bin/topics
# Ensure ~/bin is in your PATH
```

Then configure your AI agent to recognize `--topic` markers in your messages — no agent-side code required, it's a user-side convention.

### Configuration (`~/.hermes/config.yaml`)

```yaml
topic_session:
  topic_dir: ~/.topic-session/topics    # where topic files live
  sync_dir: ""                           # optional: sync to wiki/docs
```

Default: `~/.topic-session/topics/`

## Usage

### In Chat

| You type | Effect |
|----------|--------|
| `question --topic name` | Start a new topic or continue existing |
| `continue --topic name` | Resume a topic (AI reads history, gives summary) |
| `--topic --list` | List all topics |
| `--topic ls` | Same as above |
| `--topic <number>` | Select by number (#1 = most recent) |
| `--topic <keyword>` | Filter and list by keyword |

### From Terminal

```bash
topics                     # FZF interactive browser (requires fzf)
topics --list              # Plain text list
ls ~/.topic-session/topics/  # Direct file access
```

### Export to Document

```bash
# In chat:
export this as a document --topic topic-name
```

## File Format

Each topic is a Markdown file with YAML frontmatter:

```yaml
---
topic: Industry Agent Technical Routes
created: 2026-05-30
updated: 2026-05-30
domain: AI-Agent
status: active
sessions: 3
tags:
  - agent-architecture
  - RAG
  - skill-ecosystem
summary: Analysis of technical routes for building industry agents...
---
```

File name: `{topic-name}-{YYYYMMDD}.md`

The date suffix reflects the last update. Updated automatically on cross-session continuation.

## Project Structure

```
~/.topic-session/
├── topics/
│   ├── Industry-Agent-Technical-Routes-20260530.md
│   └── ...
└── scripts/
    └── topic-select.py
```

## Dependencies

- **Python 3.8+** — for the terminal browser
- **fzf** *(optional)* — interactive terminal browsing
  ```bash
  brew install fzf      # macOS
  sudo apt install fzf  # Linux
  ```

## vs `--note` (if your AI supports both)

| Marker | Purpose | Granularity |
|--------|---------|-------------|
| `--note` | Capture a single sentence or quote | Fragment |
| `--topic` | Manage a full conversation thread | Conversation |

Can be used together without conflict.

## Why use it

- **No vendor lock-in** — just Markdown files and a convention
- **Human-readable** — open with any text editor, grep, or Obsidian
- **Cross-session** — pick up exactly where you left off
- **Structured metadata** — YAML frontmatter for tags, domain, status
- **Terminal friendly** — `topics` command for quick browsing

## License

MIT
