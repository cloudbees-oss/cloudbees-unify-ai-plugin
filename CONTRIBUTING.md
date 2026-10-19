# Contributing

## Project layout

```text
plugin.json                         Portable ChatGPT/Cursor plugin manifest
mcp.json                            ChatGPT/Cursor streamable HTTP MCP config
.claude-plugin/plugin.json          Claude Code plugin manifest
.claude-plugin/marketplace.json     Claude Code marketplace entry
.mcp.json                           Claude Code MCP config
skills/<name>/SKILL.md              Shared skill instructions
skills/<name>/agents/openai.yaml    ChatGPT skill metadata and MCP dependency
hooks/                              Claude-only SessionStart guidance
scripts/build_chatgpt_plugin.py     Public ChatGPT ZIP builder
scripts/validate_plugin_layout.py   Cross-host package validator
```

Do not make `mcp.json` and `.mcp.json` identical. ChatGPT uses
`streamable-http`, OpenAI OAuth extensions, and no request headers. Claude keeps
its existing HTTP config, toolset header, and OAuth shape.

## Adding or updating a skill

1. Create or edit `skills/<skill-name>/SKILL.md`.
2. Keep `name`, `description`, and any Claude `allowed-tools` frontmatter valid.
3. Use host-neutral connection and recovery instructions in the skill body.
4. When the skill requires Unify, add `skills/<skill-name>/agents/openai.yaml`
   with this dependency:

```yaml
dependencies:
  tools:
    - type: mcp
      value: unify-mcp-server
      description: Access CloudBees Unify.
      transport: streamable_http
      url: https://mcp.cloudbees.io/v1/mcp
```

5. If a workflow needs repository information, support both local repository
   inspection and explicit user-provided URL/branch inputs.

## OAuth contract

ChatGPT must use `public-mcp-client` as a public client:

```text
mode: provided
clientId: public-mcp-client
tokenEndpointAuthMethod: none
clientSecret: absent
```

Do not add a secret or static MCP headers to `mcp.json`. The Claude `.mcp.json`
continues to send `X-MCP-Toolsets: all`.

## Versioning

Bump the version in all three plugin manifests together:

- `plugin.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

## Local validation

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_plugin_layout.py
python3 scripts/build_chatgpt_plugin.py
unzip -l dist/cloudbees-unify-chatgpt.zip
claude plugin validate . --strict
```

The ChatGPT ZIP must not contain `.claude-plugin/`, `.mcp.json`, or `hooks/`.

## Release checks

Before submitting to ChatGPT:

1. Test OAuth using `public-mcp-client` and the exact callback URL shown by
   ChatGPT.
2. Verify headerless tool discovery and read-only tool execution.
3. Verify write-tool confirmation behavior and MCP tool annotations.
4. Review all OpenAI listing metadata in `plugin.json`.
5. Add approved branding assets and current reviewer credentials in the
   submission portal.

Before releasing Claude support, install the repository through Claude Code and
verify the SessionStart hook, MCP OAuth, and one Unify tool call.
