# Topic Session

跨会话对话管理的 Hermes Agent Skill。

一句话：**在 AI 对话中用 `--topic 话题名` 标记话题，自动归档、跨会话追溯、终端交互浏览。**

---

## 解决的问题

普通 AI 对话是"流式的"——聊完就没了。下次想继续同一个话题，要么靠 AI 的记忆（不可靠），要么重头聊（浪费）。

Topic Session 把每一轮对话的关键讨论**结构化地持久化到文件**，跨会话可追溯、可搜索、可整理。效果：

```
对话中                                文件系统
───                                   ────
你: 分析一下技术路线 --topic 行业Agent     → 行业Agent-20260530.md
                                            ↑ Q: 技术路线分析
                                            ↑ A: 分层混合架构...
你: 接着说（新会话）                      → 行业Agent-20260531.md
继续 --topic 行业Agent                      ↑ Q: RAG vs 训练
（我自动读取之前内容，给摘要问从哪里继续）     ↑ A: 数据飞轮...
```

## 快速开始

### 安装

```bash
git clone https://github.com/<你的用户名>/topic-session.git
cd topic-session

# 方式一：作为 Hermes Skill 安装
hermes skills install SKILL.md

# 方式二：手动复制
cp scripts/topic-select.py ~/.hermes/scripts/
cp SKILL.md ~/.hermes/skills/
```

### 配置

在 `~/.hermes/config.yaml` 中添加：

```yaml
topic_session:
  topic_dir: ~/.topic-session/topics    # 话题文件存放目录（默认）
  sync_dir: ~/wiki                      # （可选）同步到 Obsidian wiki
  sync_domain: LLM-Agent/topics         # （可选）wiki 子路径
  editor: code                          # （可选）编辑话题文件的命令
```

如果留空，使用默认路径 `~/.topic-session/topics/`。

### 终端工具

```bash
# 安装 topic-select 到 PATH
chmod +x install.sh && ./install.sh

# 使用
topics                          # FZF 交互式浏览
topics --list                   # 文本列表
```

## 使用方法

### 在对话中

| 输入 | 效果 |
|------|------|
| `问题 --topic 话题名` | 创建新话题，或继续已有话题 |
| `继续 --topic 话题名` | 继续已有话题 |
| `--topic --list` | 列出所有话题 |
| `--topic ls` | 同上 |
| `--topic <数字>` | 按编号选中话题（#1 = 最近更新） |
| `--topic <关键词>` | 按关键词过滤并列出 |

### 在终端

```bash
topics                          # FZF 交互式选择
topics --list                   # 文本列表
ls ~/.topic-session/topics/     # 直接查看文件
```

### 整理为文档

```bash
# 在对话中
帮我整理成文档 --topic 话题名

# 在终端
cat ~/.topic-session/topics/话题名-20260530.md
```

## 文件格式

每个话题是一个 Markdown 文件，头部包含 YAML 元信息：

```yaml
---
topic: 行业Agent技术路线
created: 2026-05-30
updated: 2026-05-30
domain: LLM-Agent
status: active
sessions: 1
tags:
  - agent-architecture
  - industry-model
summary: 分析行业Agent的两条技术路线...
---
```

文件名：`{归一化话题名}-{YYYYMMDD}.md`

日期后缀 = 最后更新日期，每次跨会话追加后自动更新。

## 文件目录结构

```
~/.topic-session/
├── topics/
│   ├── 行业Agent技术路线-20260530.md
│   └── ...
└── scripts/
    └── topic-select.py
```

## 依赖

- Python 3.8+
- PyYAML（可选，不装则用正则解析）
- fzf（可选，用于 `topics` 交互式浏览）

```bash
# 可选依赖
pip install pyyaml
brew install fzf      # macOS
apt install fzf       # Linux
```

## 与 `--note` 的区别

| 标记 | 用途 | 粒度 |
|------|------|------|
| `--note` | 单句/段落的快速捕捉 | 片段级 |
| `--topic` | 整轮对话的结构化管理 | 对话级 |

两者可同时使用，互不冲突。

## License

MIT
