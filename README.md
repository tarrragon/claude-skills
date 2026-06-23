# Claude Code Skills

Reusable skill library for [Claude Code](https://claude.ai/claude-code) projects. 51 self-contained skills covering decision frameworks, development workflows, code quality, writing, and more.

Each skill is a directory with a `SKILL.md` that Claude Code automatically loads when relevant to your task.

## Quick Start

### Install a single skill

```bash
# Option 1: skill-sync CLI (recommended)
skill-sync pull wrap-decision

# Option 2: manual
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/tarrragon/claude-skills.git /tmp/cs
cd /tmp/cs && git sparse-checkout set wrap-decision
cp -r wrap-decision /your/project/.claude/skills/
rm -rf /tmp/cs
```

### Install all skills

```bash
git clone https://github.com/tarrragon/claude-skills.git .claude/skills/
```

## skill-sync CLI

A lightweight CLI for managing skills from this repo.

```bash
# Install (requires uv)
uv tool install "git+https://github.com/tarrragon/claude-skills.git#subdirectory=skill-sync"

# Commands
skill-sync list                    # List all available skills
skill-sync pull <name>             # Pull a skill to .claude/skills/
skill-sync push <name>             # Push local changes back
```

Environment variable `SKILL_SYNC_REPO` overrides the default repo URL.

## Available Skills (51)

### Decision & Analysis

| Skill | Description |
|-------|-------------|
| `wrap-decision` | WRAP decision framework - cognitive bias protection |
| `5w1h-decision` | 5W1H systematic decision-making |
| `design-decision-framework` | Multi-option evaluation for architecture decisions |
| `cognitive-load-assessment` | Task complexity evaluation |
| `decision-tree-helper` | Quick complexity assessment and dispatch suggestions |

### Development Workflow

| Skill | Description |
|-------|-------------|
| `tdd` | TDD full workflow (Phase 0-4) |
| `spec` | Requirements completeness quality gate |
| `pre-fix-eval` | Pre-fix evaluation for test failures |
| `evidence-driven-bugfix` | Evidence-driven debugging workflow |
| `tech-debt-capture` | Technical debt capture and ticket creation |
| `scope-confirmation` | Feature scope confirmation |
| `requirement-protocol` | Requirement clarification protocol |

### Project Management

| Skill | Description |
|-------|-------------|
| `ticket` | Unified ticket system (create/track/handoff/resume) |
| `doc` | Requirements tracking (proposals/spec/usecases) |
| `doc-flow` | Documentation system (CHANGELOG, worklog, tickets) |
| `version-release` | Version release workflow |
| `framework-issue` | Framework issue tracking |
| `bulk-evaluate` | Task splitting and context offloading |
| `dispatch-strategy-review` | Dispatch strategy review |

### Git & Environment

| Skill | Description |
|-------|-------------|
| `worktree` | Git worktree management |
| `branch-worktree-guardian` | Git branch and worktree management |
| `project-init` | Development environment setup |
| `startup-check` | Session startup check |
| `skill-sync` | Skill sync CLI (pull/push/list) |

### Writing & Documentation

| Skill | Description |
|-------|-------------|
| `compositional-writing` | Atomic, intent-revealing writing (Zettelkasten) |
| `methodology-writing` | Methodology writing guide |
| `multi-round-review` | Multi-round agent reviewer audit |
| `teaching-sync` | Repo-to-teaching article sync |

### Code Quality & Review

| Skill | Description |
|-------|-------------|
| `parallel-evaluation` | Multi-perspective code review |
| `test-assertion-design` | Assertion design framework |
| `search-tools-guide` | Search tools guide (MCP/LSP/grep) |
| `lsp-first` | LSP-first development strategy |
| `skill-design-guide` | Skill creation guide |
| `continuous-learning` | Reusable pattern extraction |
| `error-pattern` | Error pattern knowledge base |
| `cc-release-impact-review` | Claude Code release notes assessment |

### Agent & Collaboration

| Skill | Description |
|-------|-------------|
| `agent-team` | Agent team collaboration guide |
| `strategic-compact` | Context compression tool |
| `broken-link-check` | Broken link detection |
| `mermaid-ascii` | Mermaid diagram ASCII rendering |

### Frontend & UI

| Skill | Description |
|-------|-------------|
| `frontend-with-playwright` | Frontend dev + Playwright verification |
| `impeccable` | UI/UX design, critique, and polish |
| `style-guardian` | Design system enforcement |
| `chrome-extension-mcp-debug` | Chrome Extension debug workflow |

### Platform-Specific

| Skill | Description |
|-------|-------------|
| `provider-architecture` | Riverpod Provider architecture (Flutter) |
| `security-review` | Security review (Flutter/Dart) |
| `test-async-guardian` | Async test management (Flutter/Dart) |
| `i18n-checker` | Hardcoded string scanning for i18n |
| `saas-tech-selection` | SaaS tech stack selection |
| `data-extraction` | Web scraping strategy design |
| `zellij` | Zellij terminal multiplexer |

## Selective Sync (for framework users)

If you use the [tarrragon/claude](https://github.com/tarrragon/claude) framework, create `.claude/sync-skills.yaml`:

```yaml
mode: select       # all (default) | select | none
include:
  - wrap-decision
  - tdd
  - ticket
private:            # never pushed to any public repo
  - my-company-tool
```

| mode | Pull | Push |
|------|------|------|
| `all` (default) | All skills | All except private |
| `select` | Only `include` list | Only `include` except private |
| `none` | No skills | No skills |

## Contributing

1. Fork this repository
2. Add or modify a skill directory
3. Submit a pull request

### Skill Structure

```
your-skill/
├── SKILL.md              # Required: skill definition
├── references/            # Optional: supporting docs
├── hooks/                 # Optional: skill-specific hooks
└── pyproject.toml         # Optional: CLI tool
```

## License

MIT
