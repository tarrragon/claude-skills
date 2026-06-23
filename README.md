# Claude Code Skills

Reusable skill library for [Claude Code](https://claude.ai/claude-code) projects.

Each skill is a self-contained directory with a `SKILL.md` that Claude Code automatically loads when relevant to your task.

## Installation

### Install all skills

```bash
git clone https://github.com/tarrragon/claude-skills.git .claude/skills/
```

### Install a single skill

```bash
# Using skill-sync CLI (recommended)
skill-sync pull wrap-decision

# Or manually
git clone --depth 1 --filter=blob:none --sparse https://github.com/tarrragon/claude-skills.git /tmp/claude-skills-temp
cd /tmp/claude-skills-temp && git sparse-checkout set wrap-decision
cp -r wrap-decision /path/to/your/project/.claude/skills/
rm -rf /tmp/claude-skills-temp
```

### Using skill-sync CLI

Install the `skill-sync` CLI for easier management:

```bash
# Install (requires uv)
uv tool install "path/to/skill-sync"

# Pull a skill
skill-sync pull wrap-decision

# Push local changes
skill-sync push wrap-decision

# List available skills
skill-sync list
```

## Available Skills

### Decision & Analysis Frameworks

| Skill | Description |
|-------|-------------|
| `wrap-decision` | WRAP decision framework - cognitive bias protection and option expansion |
| `5w1h-decision` | 5W1H systematic decision-making tool |
| `design-decision-framework` | Multi-option evaluation for architecture decisions |
| `cognitive-load-assessment` | Cognitive load assessment and task complexity evaluation |
| `decision-tree-helper` | Quick task complexity assessment and dispatch suggestions |

### Development Workflow

| Skill | Description |
|-------|-------------|
| `tdd` | TDD full workflow guide (Phase 0-4) |
| `spec` | Requirements completeness quality gate |
| `pre-fix-eval` | Pre-fix evaluation system for test failures |
| `evidence-driven-bugfix` | Evidence-driven debugging workflow |
| `tech-debt-capture` | Automated technical debt capture and ticket creation |
| `scope-confirmation` | Feature scope confirmation tool |

### Writing & Documentation

| Skill | Description |
|-------|-------------|
| `compositional-writing` | Atomic, intent-revealing writing (Zettelkasten) |
| `methodology-writing` | Methodology writing guide |
| `multi-round-review` | Multi-round agent reviewer audit workflow |
| `teaching-sync` | Repo-to-teaching article bidirectional sync |

### Code Quality & Review

| Skill | Description |
|-------|-------------|
| `parallel-evaluation` | Multi-perspective code review (3-person panel) |
| `test-assertion-design` | Assertion design judgment framework |
| `dispatch-strategy-review` | Dispatch strategy review tool |
| `search-tools-guide` | Search tools usage guide (MCP/LSP/grep) |
| `lsp-first` | LSP-first development strategy |

### Agent & Team Collaboration

| Skill | Description |
|-------|-------------|
| `agent-team` | Agent team collaboration and dispatch guide |
| `requirement-protocol` | Requirement clarification to implementation protocol |
| `cc-release-impact-review` | Claude Code release notes impact assessment |

### Specialized

| Skill | Description |
|-------|-------------|
| `data-extraction` | Web scraping and data extraction strategy design |

## Contributing

1. Fork this repository
2. Create your skill directory with a `SKILL.md`
3. Submit a pull request

### Skill Structure

```
your-skill/
├── SKILL.md              # Required: skill definition (triggers, description)
├── references/            # Optional: supporting documentation
│   ├── guide.md
│   └── examples.md
└── hooks/                 # Optional: skill-specific hooks
```

## License

MIT
