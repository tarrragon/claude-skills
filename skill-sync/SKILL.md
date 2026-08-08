---
name: skill-sync
description: 'Sync Claude Code skills between local .claude/skills/ and a remote skills repository. Use for: pulling skills from remote, pushing local skills to remote, listing available remote skills.'
---

# skill-sync

Sync Claude Code skills between local `.claude/skills/` and a remote skills repository.

## Installation

```bash
uv tool install --from .claude/skills/skill-sync skill-sync
```

## Commands

| Command | Description |
|---------|-------------|
| `skill-sync pull` | Auto-compare all installed skills with remote versions.json, pull outdated ones automatically. Conflicts (local newer) are reported but not modified |
| `skill-sync pull <name>` | Pull a specific skill from the remote repo to `.claude/skills/<name>/` |
| `skill-sync push <name>` | Push a local skill to the remote repo. Remote-only files are kept |
| `skill-sync push <name> --prune` | Push, and delete files that exist only on the remote. Use after deleting or renaming files locally, otherwise the removal never reaches other consumers |
| `skill-sync list` | List all available skills in the remote repo |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SKILL_SYNC_REPO` | `https://github.com/tarrragon/claude-skills.git` | Remote skills repository URL |

## Notes

- `project-integration/` subdirectories are excluded from both pull and push operations, and `--prune` cannot reach them
- Deletion is opt-in on purpose: keeping remote-only files by default protects upstream content from being wiped by a stale local copy, at the cost of local deletions not propagating until `--prune` says so
- This tool has zero framework dependencies and works in any project

---

**Version**: 1.2.0 — `push` 新增 `--prune`：顯式刪除遠端獨有檔案，預設仍保留。原本 push 對 remote-only 檔案一律保留，使本地的刪除與更名永遠傳不到遠端（0.2.1-W3-349 實證：canonical 庫殘留 4 個本地已刪除或更名的 ticket hook，會被其他 consumer pull 下去）。同時抽出 `build_parser()`，讓引用 skill-sync 命令的下游能以測試釘住子命令存在性。
**Version**: 1.1.0
