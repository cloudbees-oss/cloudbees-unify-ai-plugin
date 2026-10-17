# ChatGPT Plugin Compatibility Design

## Goal

Make the CloudBees Unify agent plugin installable and usable in ChatGPT while
preserving its existing Claude Code behavior, packaging, OAuth client identity,
skills, and SessionStart guidance.

## Constraints

- The Unify MCP server remains `https://mcp.cloudbees.io/v1/mcp`.
- OAuth must use `public-mcp-client` as a public client.
- The public client has no client secret and uses token endpoint authentication
  method `none`.
- Claude Code continues to consume `.claude-plugin/plugin.json`, `.mcp.json`,
  the shared skills, and the existing lifecycle hook.
- A public ChatGPT submission must not contain lifecycle hooks or nonempty MCP
  request headers.
- The existing untracked Cursor-oriented files are user work and must be
  incorporated carefully rather than discarded.

## Considered Approaches

### 1. One identical package for every host

This would minimize packaging logic, but it cannot satisfy both hosts. Claude
uses a lifecycle hook and its current MCP configuration shape, while a public
ChatGPT package must omit lifecycle hooks and use the OpenAI portable MCP
schema. This approach is rejected.

### 2. Separate repositories

Independent repositories would provide complete isolation, but shared skills
and documentation would drift. Every skill change would require synchronization
and duplicated validation. This approach is rejected.

### 3. One source repository with host-specific release artifacts

This keeps one canonical set of skills and metadata while retaining
host-specific manifests and packaging boundaries. Automated validation prevents
the two releases from drifting. This is the selected approach.

## Architecture

The repository has three layers:

1. **Shared source**
   - `skills/`
   - portable descriptions and workflow instructions
   - common plugin identity and version

2. **Claude package**
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
   - `.mcp.json`
   - `hooks/`
   - shared `skills/`

3. **ChatGPT package**
   - root `plugin.json`
   - root `mcp.json`
   - shared `skills/`
   - no `hooks/`
   - no `.claude-plugin/`
   - no `.mcp.json`

A Python packaging script creates the ChatGPT ZIP from an explicit allowlist.
The allowlist prevents Claude lifecycle hooks or private development files from
entering a public submission accidentally.

## MCP Configuration

Claude retains the current `.mcp.json` configuration, including:

- `type: http`
- `X-MCP-Toolsets: all`
- `oauth.clientId: public-mcp-client`

ChatGPT receives a separate `mcp.json` using:

- the Agent Plugins 1.0 MCP schema
- `type: streamable-http`
- the same Unify MCP URL
- no static request headers
- `extensions.com.openai.auth.type: oauth`
- `extensions.com.openai.auth.client.mode: provided`
- `extensions.com.openai.auth.client.clientId: public-mcp-client`
- `extensions.com.openai.auth.client.tokenEndpointAuthMethod: none`
- no client secret

Because the public ChatGPT package cannot include
`X-MCP-Toolsets: all`, the Unify MCP service must expose the required tools
without that header for ChatGPT clients. Repository validation will make this
external dependency explicit but cannot implement the server-side behavior.

## Skill Portability

The skill bodies remain shared.

`list-components` requires only host-neutral wording changes.

`onboard-repo-to-unify` supports two execution paths:

- If the host has access to a local repository, obtain the remote URL and
  default branch with Git.
- Otherwise, ask the user for the repository URL and default branch.

Claude-specific recovery commands such as `/mcp` and `/reload-plugins` are
replaced with host-neutral instructions. Claude `allowed-tools` frontmatter may
remain because it preserves Claude permissions and does not change the skill
workflow.

Each MCP-dependent skill receives `agents/openai.yaml` metadata declaring its
Unify MCP dependency and providing concise ChatGPT discovery metadata.

The dependency entry uses `value: unify-mcp-server`, with `description`,
`transport`, and `url` as sibling fields.

## Validation and Packaging

The validator enforces:

- matching plugin names and versions
- the existing Claude MCP contract
- the separate ChatGPT MCP contract
- public-client OAuth with no client secret
- absence of ChatGPT MCP headers
- host-neutral shared skill content
- required OpenAI skill metadata

The packaging test opens the generated ZIP and verifies that it includes the
portable manifests and skills but excludes:

- `hooks/`
- `.claude-plugin/`
- `.mcp.json`
- tests and development documentation

Claude validation remains a separate check using `claude plugin validate`.

## Documentation

The README and contributing guide will describe:

- supported hosts and which files each host consumes
- ChatGPT private testing through a custom MCP connection
- the generated public-submission ZIP
- the requirement that the Unify server work without the toolset header for
  ChatGPT
- synchronized versioning and validation commands
- the fact that the Claude SessionStart hook is intentionally absent from the
  ChatGPT artifact

## Error Handling

Validation fails with a specific message when a manifest, OAuth field, skill
metadata file, or packaging boundary is incorrect.

The packaging script removes and recreates only its exact output ZIP. It does
not delete or rewrite source files.

Network-level OAuth discovery and live MCP behavior are documented as manual
smoke tests because this workspace cannot currently resolve the Unify MCP
hostname.

## Success Criteria

- Automated tests and the package-layout validator pass.
- Claude marketplace validation continues to pass.
- The ChatGPT ZIP contains no hooks or custom MCP headers.
- ChatGPT configuration identifies `public-mcp-client` as a public OAuth client
  without a secret.
- Both skills contain host-neutral operational guidance.
- Documentation explains the remaining server-side and publication checks.
