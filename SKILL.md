---
name: topic-session
description: 跨会话对话管理。用 --topic 话题名 标记对话，自动归档、跨会话追溯、终端浏览。
metadata:
  hermes:
    tags: [topic, session, note, knowledge-management]
    category: note-taking
---

# Topic Session Skill

用 `--topic 话题名` 管理跨会话的 AI 对话。自动归档、可追溯、可整理。

> **配置**：`~/.hermes/config.yaml` 中设置 `topic_session.topic_dir`，默认 `~/.topic-session/topics/`

---

## 触发条件

### 方式一：消息末尾标记

```
问题 --topic 话题名
继续 --topic 话题名
帮我整理成文档 --topic 话题名
```

### 方式二：对话框内操作

| 输入 | 效果 |
|------|------|
| `--topic --list` | 列出所有话题 |
| `--topic ls` | 同上 |
| `--topic <关键词>` | 过滤并列出 |
| `--topic <数字>` | 按编号选中（#1 = 最近更新） |
| `继续 <编号>` | 同上 |
| `继续 --topic 话题名` | 直接继续已有话题（跳过列表步骤） |

### 方式三：会话范围模式

| 输入 | 效果 |
|------|------|
| `--topic start 话题名` | 进入话题范围模式，写入 `.active` 标记文件 |
| `--topic end` | 退出范围模式，删除 `.active` 标记文件 |
| `--topic 话题名`（单次） | 同方式一，同时更新 `.active` |

**核心机制**：进入范围模式后，后续不带 `--topic` 的消息自动归入该话题，无需重复输入。跨会话持久。

详见下方"Session Range 模式"章节。

---

## 操作流程

### 提取话题名

解析用户消息中的 `--topic <xxx>`：
- `--topic xxx` → 话题名 = xxx
- `--topic <纯数字>` → 扫描目录，按 mtime 倒序，取第 N 个
- `--topic --list` / `--topic ls` → 列出所有话题

### 文件路径

话题文件存放在 `topic_session.topic_dir`（默认 `~/.topic-session/topics/`）。

目录不存在则自动创建。

### 创建/追加

1. **话题名归一化** → 得到 base name
   - 中文原样保留
   - 英文空格转 `-`
   - 特殊字符（`/ \ : * ? " < > |`）转 `-`
2. **搜索已有文件**：`{base_name}-*.md`
3. **存在**：取最新文件 → 读取 → 给摘要 → 问从哪里继续
4. **不存在**：创建新文件，写入 YAML header
5. 每次回复后追加 Q/A 条目
6. 日期变化时重命名文件（更新日期后缀）
7. 如果配置了 `sync_dir`，同步到 `{sync_dir}/{sync_domain}/{文件名}`

### 继续话题

1. 读取话题文件
2. 用最后 3-5 条 Q/A 生成摘要
3. 指出上次的待讨论点
4. 问从哪里继续

### 文件格式

```yaml
---
topic: 话题名
created: 2026-05-30
updated: 2026-05-30
domain: 领域分类
status: active
sessions: 1
tags:
  - tag1
  - tag2
summary: 一句话描述
related_topics:
  - 相关话题名-20260530.md
---
```

内容条目按日期分组，每条包含 Q + A + 要点 + 标签。

---

## Session Range 模式（会话范围管理）

通过 `.active` 标记文件，让用户无需每次对话都写 `--topic`。

### 标记文件位置

`{topic_dir}/.active`（与话题文件同目录），内容为纯文本格式的当前活跃话题名。

### 进入

```
用户: 问题 --topic start 话题名
Agent: ✅ 已进入 topic『话题名』模式，后续消息无需 --topic
```

Agent 操作：创建/打开话题文件 → 写入 `.active` → 回复确认。

### 范围模式下的无标记消息

用户不带 `--topic` 的消息，Agent 自动：

1. 检测 `.active` 文件是否存在
2. 存在 → 读取活跃话题名
3. 搜索对应话题文件 → 读取 → 生成摘要
4. 正常回复后追加 Q/A 条目

### 退出

```
用户: 内容 --topic end
Agent: 🚪 已退出 topic『话题名』模式
```

Agent 操作：删除 `.active` 文件，追加本轮内容后恢复正常对话。

### 切换

- `--topic start 新话题`（已在范围模式中）：更新 `.active` 为新话题
- `--topic 话题名`（单次）：更新 `.active`

### 跨会话

`.active` 文件跨会话持久。新对话中第一条无 `--topic` 的消息触发的检测会自动归入上次话题，并提示退出方式。

---

## 配置

```yaml
# ~/.hermes/config.yaml
topic_session:
  topic_dir: ~/.topic-session/topics    # 话题文件目录
  sync_dir: ''                          # 同步到其他目录（可选）
  sync_domain: ''                       # 同步子路径（可选）
```

---

## 与 --note 的关系

| 标记 | 用途 | 粒度 |
|------|------|------|
| `--note` | 单句捕捉 | 片段 |
| `--topic` | 对话管理 | 整轮对话 |

---

## Pitfalls

- **话题名为纯数字时**：`--topic 1` 按编号选，`--topic 话题1` 按名字搜——通过是否全为数字判断
- **日期后缀是最后更新日期**：不是创建日期。跨会话追加后自动重命名
- **sync 同步是全文件覆盖**：不是 diff 同步
- **目录不存在时先创建**：`write_file` 会自动 `mkdir -p`，但不依赖此特性
- **`.active` 文件操作控制**：仅 `--topic start`、`--topic end`、`--topic 话题名` 三种语法可操作 `.active` 文件
- **会话结束时不清除 `.active`**：跨会话持久是设计——由用户显式 `--topic end` 控制
- **`.active` 指向不存在的文件**：检测到时提示用户 `--topic end` 而非静默失败
