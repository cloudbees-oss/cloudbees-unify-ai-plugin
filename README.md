
# CloudBees Unify Agent Plugin for Claude Code, Codex, Cursor, VS Code, Copilot CLI, and Grok CLI

**Ship AI-written code faster and safer with CloudBees, right from your coding agent.**

AI agents write code faster than teams can test, release, and govern it. This plugin brings CloudBees Unify into the coding agent you already use, so the agent that writes your code can also help you test, ship, and govern it:

- **Build at AI speed:** find out why a build failed, read its logs, and see which test suites and cases broke.
- **Jenkins visibility (CloudBees CI):** list your controllers and surface disabled or out-of-date plugins and open vulnerabilities.
- **Faster, safer releases:** trigger, rerun, or stop workflows, approve manual gates, and toggle or progressively roll out feature flags by target group.
- **Govern the software factory:** review policy gate outcomes for each run, manage policies and approvals, and triage security findings against SLAs, all in one place.

The plugin connects to the Unify MCP server and adds skills for common tasks like onboarding a repository.

## Installation

### Claude Code

Install from the Claude Code marketplace (once published):

```
/plugin marketplace add cloudbees-oss/cloudbees-unify-ai-plugin
/plugin install cloudbees-unify@unify-ai-plugins
```

Or install locally from a clone:

```
git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git
claude plugin marketplace add ./cloudbees-unify-ai-plugin
claude plugin install cloudbees-unify@unify-ai-plugins
```

Once installed, open Claude and connect to Unify using the Unify MCP Server:
1. Send the `/mcp` command to Claude.
2. Select the `unify-mcp-server` server
3. Choose the Authenticate option and follow the instructions in Claude

### Claude desktop app

The desktop app uses the same marketplace. Add `cloudbees-oss/cloudbees-unify-ai-plugin`
as a plugin marketplace in the app, then install `cloudbees-unify`.

### Codex CLI

```
codex plugin marketplace add cloudbees-oss/cloudbees-unify-ai-plugin
codex plugin add cloudbees-unify@unify-ai-plugins
```

From a clone, pass the local path to `codex plugin marketplace add` instead.
Run `codex plugin list` to confirm the plugin is installed and enabled.

Then sign in to the Unify MCP server:

```
codex mcp login unify-mcp-server
```

An MCP server named `unify-mcp-server` in your own Codex configuration takes
precedence over the plugin's server. Remove it with
`codex mcp remove unify-mcp-server` to use the plugin's connection.

### Codex in the ChatGPT desktop app

The Codex app shares its plugin configuration with Codex CLI. Install the plugin
with the commands above, or add the same marketplace from the app's plugin settings.

### VS Code (Agent Plugins)

**Recommended:** Install as an Agent Plugin in VS Code 1.99+ (Copilot Chat agent mode):

1. Open the Extensions view (⇧⌘X) and search for `@agentPlugins`.
2. If published, search for `cloudbees-unify` and click **Install**.
3. To install from source, run **Chat: Install Plugin From Source** from the Command Palette and enter:

   ```
   https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git
   ```

4. The plugin will appear in the **Agent Plugins - Installed** section. Enable it if needed.

**Manual (local clone):**

1. Clone this repo:
   ```
   git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git
   ```
2. Register the plugin in your VS Code `settings.json`:
   ```json
   "chat.pluginLocations": {
     "/absolute/path/to/unify-ai-plugin": true
   }
   ```
3. Reload VS Code. The plugin will be enabled and its skills, hooks, and MCP servers will be auto-discovered.

### Cursor (desktop and CLI)

Install `cloudbees-unify` from the Cursor marketplace (once published).

Or install locally by cloning into Cursor's local plugins folder. Cursor ignores
symlinks that point outside this folder, so clone or copy the files rather than
linking them.

```
git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git \
  ~/.cursor/plugins/local/cloudbees-unify
```

In Cursor desktop, run **Developer: Reload Window**. In Cursor CLI, start a new
`cursor-agent` session. Then sign in to Unify:

1. Send the `/mcp` command.
2. Select the `unify-mcp-server` server and authenticate.
3. Complete sign-in in your browser.

### Grok CLI

Grok CLI support is in preview. Installation has been tested with a local clone
on Grok CLI 1.0.67; signing in to Unify from Grok has not been fully verified yet.

Before you start, sign in to Grok itself (run `grok` and complete the grok.com
sign-in, or use `grok login`). This is separate from signing in to Unify.

Install, trust, and enable the plugin from a clone:

```
git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git
grok plugin install /absolute/path/to/cloudbees-unify-ai-plugin --trust
grok plugin enable cloudbees-unify
grok plugin details cloudbees-unify
```

Grok also accepts a GitHub source such as
`cloudbees-oss/cloudbees-unify-ai-plugin` or
`cloudbees-oss/cloudbees-unify-ai-plugin@<ref>` in place of the local path.
`--trust` is required: without it, Grok does not load the plugin's skills, hooks,
or MCP server. `grok plugin details` should list both skills, the
`unify-mcp-server` MCP server, and the SessionStart hook.

Then sign in to the Unify MCP server:

1. Start `grok` and run `/mcps`.
2. Select `unify-mcp-server` and press `i` to authenticate. This is the step
   where Grok is expected to open a browser window for Unify sign-in.

If the plugin's skills or server don't appear, run `/plugins`, open the
**Plugins** tab, and press `r` to reload, or start a new session.

### GitHub Copilot CLI

Uses the same plugin format as above. See [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference).

## How it works

This plugin ships a `.claude-plugin/plugin.json` (Claude/VS Code compatible) and a `.mcp.json` that points at the CloudBees Unify MCP server (`https://mcp.cloudbees.io/v1/mcp`). Codex reads `.codex-plugin/plugin.json` and `.codex-plugin/mcp.json`, which points at the same server.

When enabled, VS Code, Claude Code, and Copilot CLI auto-discover:

- **Skills** (in `skills/`)
- **Hooks** (in `hooks/` or `hooks.json`)
- **MCP servers** (from `.mcp.json`)

Codex loads the same skills, hooks, and MCP server from `.codex-plugin/plugin.json`.

Grok CLI reads `.claude-plugin/plugin.json` and the same `skills/`, `hooks/`, and `.mcp.json`.

On first use, the MCP server opens a browser window for OAuth (Google, GitHub, or SSO). After that, agent tools invoke Unify transparently. On Grok CLI, the browser prompt is expected when you authenticate the server from `/mcps`; sign-in and tool calls on Grok have not been fully verified yet (see [Grok CLI](#grok-cli)).

## Usage

After installing and enabling the plugin, just ask in plain English. Claude Code, Copilot Chat, or Copilot CLI will route your request through the appropriate skill.

### Example requests

```
What components are in my CloudBees Unify org?
Show me the latest build status for the checkout-service component.
Are there any open critical security findings this week?
List feature flags for the storefront application.
Why did the last workflow run on payments-api fail? Show me the logs.
```

The first command in a session opens a browser for OAuth (Google / GitHub / SSO). After that, calls run silently.

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

## Security and permissions

- **MCP endpoint:** all hosts connect to `https://mcp.cloudbees.io/v1/mcp` over HTTPS.
- **OAuth:** the server's protected-resource metadata
  (`https://mcp.cloudbees.io/.well-known/oauth-protected-resource`) names the
  authorization server `https://id.cloudbees.io/realms/cloudbees`. The plugin
  configures the public OAuth client `public-mcp-client`. The Codex config requests
  the scopes `openid profile email mcp:unify:connect`; the other hosts set no scopes
  and use what the server advertises (`mcp:unify:connect`). Which client and scopes
  Grok CLI actually sends during sign-in has not been verified yet.
- **Credential storage:** your coding agent (Claude Code, Codex, VS Code, Copilot
  CLI, or Grok CLI) stores the resulting tokens; the plugin does not. Grok CLI
  stores them in `mcp_credentials.json` in its home directory (`~/.grok` by
  default, or `$GROK_HOME`) as plaintext with owner-only permissions; protect the
  machine with full-disk encryption.
- **Permissions:** every operation runs as you. You need a CloudBees Unify account
  with membership in the relevant organizations, and Unify's role-based access
  control decides what you can see and change.
- **Write operations:** the plugin requests all toolsets (`X-MCP-Toolsets: all`).
  Besides read-only tools, this includes tools that make changes, such as creating
  and deleting components, triggering, rerunning, and stopping workflows,
  approving or rejecting manual gates, changing feature flags, and managing
  policies, roles, and authorizations. Review what the agent proposes before
  approving these calls.
- **SessionStart hook:** on hosts that honor SessionStart `additionalContext`
  (such as Claude Code and Codex), the hook adds the short plugin guidance in
  `hooks/system-prompt.md` to the model's context. Grok CLI does not add hook
  output to the model's context, so Grok does not get that guidance; the sign-in
  and no-fabrication parts are repeated in each skill, which apply only once a
  skill is selected.

## Layout

- `.claude-plugin/`   — Claude plugin.json (also read by Grok CLI) + marketplace.json
- `.codex-plugin/`    — Codex plugin.json + mcp.json
- `.cursor-plugin/`   — Cursor plugin.json + hooks.json (MCP config is the root `mcp.json`)
- `.agents/plugins/`  — Codex marketplace.json
- `.mcp.json`         — Unify MCP server config (auto-wired on install)
- `skills/`           — skill definitions
- `hooks/`            — SessionStart hook + system prompt injected on session start (not on Grok CLI)

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills.

## Troubleshooting

- If the plugin does not appear after installation, check that the `name` field in `plugin.json` uses only lowercase letters, numbers, and hyphens.
- If skills do not load, ensure the skill directory and `SKILL.md` frontmatter use plain kebab-case names.
- If you see an OAuth prompt, this is expected on first use.
- For more, see the [Agent Plugins for VS Code documentation](https://code.visualstudio.com/docs/copilot/customization/agent-plugins).

### Cursor CLI: sign-in fails when the Claude Code plugin is also installed

If `cloudbees-unify` is installed in both Claude Code and Cursor, Cursor CLI may
pick up the Claude Code copy of the MCP server, and `/mcp` sign-in fails with:

```text
Policy 'Trusted Hosts' rejected request to client-registration service.
```

To work around it, disable or uninstall the Claude Code copy of the plugin, start
a new `cursor-agent` session, and sign in again through `/mcp`.

## License

MIT — see [LICENSE](./LICENSE).
