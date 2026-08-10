
# CloudBees Unify Agent Plugin for VS Code, Claude Code, and Copilot CLI

This repository provides a prepackaged agent plugin that lets AI coding agents (VS Code Copilot Chat, Claude Code, and Copilot CLI) talk to CloudBees Unify — including components, workflow runs, build status and logs, security findings, feature flags, CI controllers, users, and teams — via the Unify MCP server.

> Status: Scaffold. The example agent and skill are placeholders meant to be replaced as real capabilities are added.

## Installation

### Claude Code

Install from the Claude Code marketplace (once published):

```
/plugin marketplace add cloudbees-oss/cloudbees-unify-ai-plugins
/plugin install cloudbees-unify@unify-ai-plugins
```

Or install locally from a clone:

```
git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugins.git
claude plugin install ./cloudbees-unify-ai-plugins --scope user
```

Once installed, open Claude and connect to Unify using the Unify MCP Server:
1. Send the `/mcp` command to Claude.
2. Select the `unify-mcp-server` server
3. Choose the Authenticate option and follow the instructions in Claude

### VS Code (Agent Plugins)

**Recommended:** Install as an Agent Plugin in VS Code 1.99+ (Copilot Chat agent mode):

1. Open the Extensions view (⇧⌘X) and search for `@agentPlugins`.
2. If published, search for `cloudbees-unify` and click **Install**.
3. To install from source, run **Chat: Install Plugin From Source** from the Command Palette and enter:

   ```
   https://github.com/cloudbees-oss/cloudbees-unify-ai-plugins.git
   ```

4. The plugin will appear in the **Agent Plugins - Installed** section. Enable it if needed.

**Manual (local clone):**

1. Clone this repo:
   ```
   git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugins.git
   ```
2. Register the plugin in your VS Code `settings.json`:
   ```json
   "chat.pluginLocations": {
     "/absolute/path/to/unify-ai-plugins": true
   }
   ```
3. Reload VS Code. The plugin will be enabled and its skills, agents, hooks, and MCP servers will be auto-discovered.

### GitHub Copilot CLI

Uses the same plugin format as above. See [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference).

## How it works

This plugin ships a `.claude-plugin/plugin.json` (Claude/VS Code compatible) and a `.mcp.json` that points at the CloudBees Unify MCP server (`https://mcp.cloudbees.io/v1/mcp`).

When enabled, VS Code, Claude Code, and Copilot CLI auto-discover:

- **Skills** (in `skills/`)
- **Agents** (in `agents/`)
- **Hooks** (in `hooks/` or `hooks.json`)
- **MCP servers** (from `.mcp.json`)

On first use, the MCP server opens a browser window for OAuth (Google, GitHub, or SSO). After that, agent tools invoke Unify transparently.

## Usage

After installing and enabling the plugin, just ask in plain English. Claude Code, Copilot Chat, or Copilot CLI will route your request through the `unify-assistant` sub-agent and the appropriate skill.

### Example requests

```
What components are in my CloudBees Unify org?
Show me the latest build status for the checkout-service component.
Are there any open critical security findings this week?
List feature flags for the storefront application.
Why did the last workflow run on payments-api fail? Show me the logs.
```

The first command in a session opens a browser for OAuth (Google / GitHub / SSO). After that, calls run silently.

### Invoke a sub-agent explicitly

Use the `@` prefix to scope a request to the Unify assistant:

```
@unify-assistant list components in the platform-eng organization
```

### Invoke a skill directly

Skills are addressable as `/cloudbees-unify:list-components`:

```
/cloudbees-unify:list-components
/cloudbees-unify:list-components organization=platform-eng filter=api
```

### Chain Unify into a coding task

The point of running this in Claude Code or Copilot Chat is mixing Unify data with code:

```
Find the component that owns this repo in Unify, then show me the last 5 builds
  and open a diff between the last green commit and HEAD.

A Snyk finding flagged lodash in the auth-service. Pull the finding from Unify,
  then update package.json and the lockfile to the patched version.
```

## Layout

- `.claude-plugin/`   — plugin.json + marketplace.json
- `.mcp.json`         — Unify MCP server config (auto-wired on install)
- `agents/`           — sub-agent definitions
- `skills/`           — skill definitions invoked by sub-agents or directly
- `hooks/`            — SessionStart hook + system prompt injected on session start

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add agents and skills.

## Troubleshooting

- If the plugin does not appear after installation, check that the `name` field in `plugin.json` uses only lowercase letters, numbers, and hyphens.
- If skills do not load, ensure the skill directory and `SKILL.md` frontmatter use plain kebab-case names.
- If you see an OAuth prompt, this is expected on first use.
- For more, see the [Agent Plugins for VS Code documentation](https://code.visualstudio.com/docs/copilot/customization/agent-plugins).

## License

MIT — see [LICENSE](./LICENSE).

1. Clone the repo:
   ```
   git clone https://github.com/cloudbees/unify-ai-plugins.git
   ```
2. Open the folder in VS Code. Copilot Chat agent mode will discover the `.mcp.json` at the repo root.

To wire Unify into any workspace (not just this repo), copy the server entry into your VS Code user `settings.json`:

```json
{
  "github.copilot.chat.mcp.servers": {
    "unify-mcp-server": {
      "type": "http",
      "url": "https://mcp.cloudbees.io/v1/mcp",
      "oauth": {
        "clientId": "public-mcp-client"
      }
    }
  }
}
```

Then open Copilot Chat, switch to **Agent** mode, and ask a Unify question. The first call opens a browser for OAuth.

> Note: the sub-agent and skill definitions in `agents/` and `skills/` are Claude Code conventions. Copilot Chat in VS Code will use the MCP server tools directly but won't auto-load the sub-agent — you can still steer it by saying "use the unify assistant approach" or pasting in `agents/unify-assistant.md` as context.

## How it works

The plugin ships a `.mcp.json` that points at the CloudBees Unify MCP server (`https://mcp.cloudbees.io/v1/mcp`). On first use, the MCP server opens a browser window for OAuth (Google, GitHub, or SSO). After that, Claude Code / Copilot CLI invoke Unify tools transparently.

Sub-agents and skills in this repo orchestrate those MCP tools for higher-level tasks.

## Usage

After installing the plugin, just ask in plain English. Claude Code (or Copilot CLI) will route your request through the `unify-assistant` sub-agent and the appropriate skill.

### Talk to it directly

```
> What components are in my CloudBees Unify org?
> Show me the latest build status for the checkout-service component.
> Are there any open critical security findings this week?
> List feature flags for the storefront application.
> Why did the last workflow run on payments-api fail? Show me the logs.
```

The first command in a session opens a browser for OAuth (Google / GitHub / SSO). After that, calls run silently.

### Invoke a sub-agent explicitly

Use the `@` prefix to scope a request to the Unify assistant:

```
> @unify-assistant list components in the platform-eng organization
```

### Invoke a skill directly

Skills are addressable as `/<plugin>:<skill>`. The example skill ships with the scaffold:

```
/cloudbees-unify:list-components
/cloudbees-unify:list-components organization=platform-eng filter=api
```

### Chain Unify into a coding task

The point of running this in Claude Code or Copilot CLI is mixing Unify data with code:

```
> Find the component that owns this repo in Unify, then show me the last 5 builds
  and open a diff between the last green commit and HEAD.

> A Snyk finding flagged lodash in the auth-service. Pull the finding from Unify,
  then update package.json and the lockfile to the patched version.
```

## Layout

.claude-plugin/   plugin.json + marketplace.json
.mcp.json         Unify MCP server config (auto-wired on install)
agents/           sub-agent definitions
skills/           skill definitions invoked by sub-agents or directly
hooks/            SessionStart hook + system prompt injected on session start

```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add agents and skills.

## License

MIT — see [LICENSE](./LICENSE).
