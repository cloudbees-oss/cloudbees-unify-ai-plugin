# Contributing

## Project layout

```
.claude-plugin/         Plugin + marketplace manifests (consumed by Claude Code and GitHub Copilot CLI)
.mcp.json               Unify MCP server config — auto-wired when the plugin is installed
skills/<name>/SKILL.md  Skill definitions invoked directly via /<plugin>:<skill>
hooks/                  SessionStart hooks; system-prompt.md is injected on session start
```

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Frontmatter must include at minimum: `name`, `description`, `allowed-tools`.
3. Body describes inputs, steps, and notes. Be specific about which MCP tool to call.

## Local install for testing

```
claude plugin install /path/to/unify-ai-plugin --scope user
```

GitHub Copilot CLI uses the same plugin format; install via its `/plugin` flow against this directory or the published marketplace entry.

## Versioning

Bump `version` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` together — they must match.
