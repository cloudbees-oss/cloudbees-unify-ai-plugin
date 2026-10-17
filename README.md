# CloudBees Unify Agent Plugin

This repository packages the CloudBees Unify MCP integration for ChatGPT,
Claude Code, Cursor, VS Code, and GitHub Copilot CLI. It provides skills for
working with Unify components, workflows, builds, security findings, feature
flags, CI controllers, users, and teams.

## Host compatibility

| Host | Plugin manifest | MCP configuration | Lifecycle hooks |
| --- | --- | --- | --- |
| ChatGPT | `plugin.json` | `mcp.json` | Excluded from the public ZIP |
| Claude Code | `.claude-plugin/plugin.json` | `.mcp.json` | `hooks/` included |
| Cursor | `plugin.json` | `mcp.json` | Not included |
| VS Code and Copilot CLI | `.claude-plugin/plugin.json` | `.mcp.json` | Host-dependent |

The skills under `skills/` are shared. The ChatGPT and Claude MCP manifests are
deliberately different because each host uses a different package contract.

## ChatGPT

### Server prerequisites

The ChatGPT connection uses:

- MCP endpoint: `https://mcp.cloudbees.io/v1/mcp`
- Streamable HTTP transport
- OAuth client ID: `public-mcp-client`
- Public-client token endpoint authentication method: `none`
- No client secret

The authorization server must publish OAuth protected-resource and
authorization-server metadata, support PKCE with `S256`, propagate the RFC 8707
`resource` parameter, and validate token audience for the MCP resource. MCP
tools must declare OAuth `securitySchemes` and return an authentication
challenge when linking is required.

Register the exact callback URL shown in ChatGPT's MCP management page. The
stable `https://chatgpt.com/connector_platform_oauth_redirect` callback applies
when the authorization server correctly supports RFC 9207 issuer
identification; otherwise ChatGPT supplies a callback-ID-specific URL.

If access is restricted by ChatGPT workspace domain, the authorization server
must also support `openid` and `email` scopes and expose a UserInfo endpoint.

The public ChatGPT package cannot send the Claude-specific
`X-MCP-Toolsets: all` header. The deployed MCP endpoint must therefore expose
the required tools to ChatGPT without that header.

### Private test

Before publishing, add `https://mcp.cloudbees.io/v1/mcp` as a custom MCP
connection in ChatGPT Work, authenticate through the browser, and verify at
least one read-only tool call. Also test a write operation separately so the
confirmation and tool annotations can be reviewed.

### Build the submission ZIP

```bash
python3 scripts/validate_plugin_layout.py
python3 scripts/build_chatgpt_plugin.py
unzip -l dist/cloudbees-unify-chatgpt.zip
```

The generated ZIP contains only:

- `plugin.json`
- `mcp.json`
- `README.md`
- `LICENSE`
- Shared skill definitions and their `agents/openai.yaml` metadata

Claude manifests and lifecycle hooks are intentionally excluded.

### Publish to ChatGPT

1. Verify the CloudBees publisher organization and ensure the submitter has the
   required Apps Management role.
2. Verify control of `mcp.cloudbees.io` using the DNS or well-known challenge
   token supplied by the OpenAI submission flow.
3. Confirm the live MCP server exposes accurate read-only, destructive,
   open-world, and authentication annotations for every tool.
4. Prepare the listing assets: approved CloudBees icon, support and legal URLs,
   demo video, five positive test prompts, and three negative test prompts.
5. Prepare a dedicated reviewer account that does not require MFA and contains
   representative test data.
6. Build `dist/cloudbees-unify-chatgpt.zip` and upload it through the ChatGPT
   plugin submission portal.
7. Enter the listing and review information, run the automated checks, and
   submit the plugin for review.

See the official OpenAI documentation:

- https://developers.openai.com/plugins/guides/submit-claude-plugin
- https://developers.openai.com/plugins/deploy/submission
- https://developers.openai.com/plugins/deploy/app-review

## Claude Code

Install from the Claude Code marketplace once published:

```text
/plugin marketplace add cloudbees-oss/cloudbees-unify-ai-plugin
/plugin install cloudbees-unify@unify-ai-plugins
```

Or install from a local clone:

```bash
git clone https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git
claude plugin install ./cloudbees-unify-ai-plugin --scope user
```

Then run `/mcp`, select `unify-mcp-server`, and complete authentication. Claude
continues to use `.mcp.json`, including `X-MCP-Toolsets: all`, and receives the
existing SessionStart guidance from `hooks/`.

## Cursor

Install from source using Cursor's agent-plugin flow, or place the repository in
Cursor's local plugin directory. Cursor consumes the portable `plugin.json` and
`mcp.json`; complete the browser OAuth flow on first use.

## VS Code and GitHub Copilot CLI

For VS Code, use **Chat: Install Plugin From Source** and provide:

```text
https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin.git
```

GitHub Copilot CLI can install the same repository through its plugin flow.

## Example requests

```text
What components are in my CloudBees Unify organization?
Show the latest build status for the checkout-service component.
Are there open critical security findings this week?
Why did the last workflow run on payments-api fail?
Onboard this repository to Unify and start a security scan.
```

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_plugin_layout.py
python3 scripts/build_chatgpt_plugin.py
claude plugin validate . --strict
```

## License

MIT — see [LICENSE](./LICENSE).
