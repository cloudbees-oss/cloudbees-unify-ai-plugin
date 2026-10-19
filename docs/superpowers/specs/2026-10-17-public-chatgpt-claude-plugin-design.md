# Public ChatGPT and Claude Plugin Design

## Goal

Prepare the CloudBees Unify plugin for public distribution through the ChatGPT
Plugin Directory while preserving the existing Claude Code installation and
runtime behavior.

The repository will remain the single source of truth for shared skills, plugin
identity, and versioning. Host-specific manifests, authentication metadata,
packaging, and validation will remain separate.

## Scope

This work covers:

- a public ChatGPT submission artifact;
- the existing Claude Code marketplace package;
- shared skills that work in both hosts;
- OpenAI listing metadata and review materials stored in the repository;
- automated checks that prevent host-specific files from leaking between
  packages;
- documented live checks for OAuth, tool discovery, and submission review.

The work does not publish the plugin, create production reviewer credentials,
register DNS records, or modify the deployed Unify MCP server.

## Considered Approaches

### One repository with host-specific packages

Keep shared skills in one place and produce separate ChatGPT and Claude package
surfaces. This avoids duplication while allowing each host to use its required
manifest and authentication format.

This is the selected approach.

### Submit the Claude package for conversion

Use the existing Claude package as the primary submission input and rely on the
OpenAI submission flow to translate it. This reduces repository work but gives
less control over OpenAI-specific metadata, package boundaries, and automated
validation.

This approach is not selected.

### Split ChatGPT and Claude into separate repositories

Maintain independent repositories for each host. This provides complete
isolation but would duplicate skills, documentation, tests, and release
coordination.

This approach is not selected.

## Repository Architecture

The repository has three layers.

### Shared source

- `skills/*/SKILL.md`
- skill-specific references or scripts when genuinely needed
- common plugin name and synchronized version
- general documentation and examples

Shared skill instructions must remain host-neutral. They may describe outcomes,
inputs, error handling, and authorization boundaries, but must not require a
host-specific command.

### ChatGPT package

- `plugin.json`
- `mcp.json`
- shared `skills/`
- `skills/*/agents/openai.yaml`
- public documentation and license files
- approved package-local branding assets, if required by the final submission
  format

The public artifact is built from an explicit allowlist. It excludes Claude
manifests, lifecycle hooks, local configuration, tests, development plans,
credentials, and generated diagnostics.

### Claude package

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.mcp.json`
- `hooks/`
- shared `skills/`

Claude retains its current MCP header, OAuth shape, marketplace commands, and
SessionStart behavior unless a Claude-specific validation failure requires a
change.

## Authentication

### ChatGPT

`mcp.json` declares the hosted Unify MCP server and OpenAI OAuth extension. The
client is the predefined public client `public-mcp-client`, with no client
secret and token endpoint authentication method `none`.

Public ChatGPT authentication is driven by `mcp.json`, the deployed protected
resource and authorization-server metadata, and the settings entered during
submission. It is not driven by the Claude marketplace manifest.

The deployed authentication system must:

- return an OAuth challenge for unauthenticated MCP requests;
- publish protected-resource metadata for the MCP resource;
- publish authorization-server metadata;
- support authorization code with PKCE `S256`;
- support the configured public-client token endpoint authentication method;
- preserve the MCP resource value through authorization and token exchange;
- issue tokens with the expected audience;
- accept the exact callback URI used by the ChatGPT submission;
- expose `openid`, `email`, and UserInfo behavior when workspace-domain
  restrictions require them.

Live OAuth checks remain release gates because repository tests cannot prove
the deployed server behavior.

### Claude

`.mcp.json` continues to declare `public-mcp-client` using Claude's supported
OAuth configuration. It retains `X-MCP-Toolsets: all` unless the Claude
integration no longer requires that header.

The public ChatGPT artifact must not inherit this Claude-specific header.

### Marketplace authentication policy

Installation policies belong to a marketplace entry and affect marketplace
installation behavior. They are separate from public ChatGPT MCP
authentication.

If an OpenAI-compatible marketplace manifest is added for local Codex testing,
it will explicitly use `ON_INSTALL` or `FIRST_USE` based on the desired test
experience. It will not replace the OAuth declaration in `mcp.json`.

## Skills

The existing `list-components` and `onboard-repo-to-unify` skills remain shared.
Following the skill-creator guidance:

- descriptions stay concise and discriminating;
- skill bodies contain only non-obvious workflow guidance;
- connection recovery uses host-neutral language;
- MCP dependencies are declared in `agents/openai.yaml`;
- Claude `allowed-tools` metadata is preserved where it controls Claude
  permissions;
- no skill implies permission for external writes beyond the user's request;
- no redundant README or reference files are added to individual skills.

OpenAI UI metadata must remain consistent with each skill's actual behavior and
must reference the fixed MCP server name `unify-mcp-server`.

## Public Submission Materials

The repository will track a submission checklist and non-secret review
materials:

- plugin name, descriptions, category, capabilities, support URL, website URL,
  privacy policy URL, and terms URL;
- approved icon or logo assets in required sizes and formats;
- five representative positive test prompts;
- three negative prompts that demonstrate correct refusal or non-routing;
- demo-video preparation requirements;
- domain-verification requirements;
- reviewer-account requirements without storing credentials;
- accurate read-only, destructive, open-world, and authentication annotations
  for every exposed MCP tool.

Secrets, reviewer passwords, OAuth tokens, and unpublished verification tokens
must not be committed.

## Packaging

The ChatGPT builder uses an explicit allowlist rather than copying the
repository recursively. The build fails when a required file is missing or
invalid.

The artifact must include only files required for ChatGPT execution,
documentation, and review. Package inspection verifies that it excludes:

- `.claude-plugin/`;
- `.mcp.json`;
- `hooks/`;
- local host settings;
- test fixtures and implementation plans;
- credentials and temporary files.

Claude continues to install from the repository or Claude marketplace layout
and does not consume the generated ChatGPT archive.

## Validation

Automated validation will cover:

- parseable JSON and YAML;
- matching plugin names and versions;
- required OpenAI interface metadata;
- the ChatGPT MCP URL, transport, OAuth client, and absence of secrets;
- the preserved Claude MCP URL, header, and OAuth client;
- OpenAI skill dependency metadata;
- host-neutral skill instructions;
- required public-submission review materials;
- exact ChatGPT archive contents;
- exclusion of Claude-only and sensitive files;
- successful execution of the package validator and unit tests.

Separate validation commands will check:

- the repository's Python unit tests;
- the cross-host package validator;
- the generated ChatGPT archive;
- Claude's strict plugin validator;
- JSON parsing and repository whitespace.

Live smoke tests will verify:

- ChatGPT OAuth and callback handling;
- headerless tool discovery;
- one read-only Unify operation;
- one write operation with the expected confirmation behavior;
- Claude OAuth and one Unify tool call;
- tool annotations visible to the ChatGPT review system.

## Error Handling

Validation errors must identify the affected host, file, and violated contract.
The builder must fail closed when package contents are ambiguous.

Authentication failures are reported by boundary:

- package metadata;
- protected-resource discovery;
- authorization-server discovery;
- client registration or predefined client configuration;
- browser authorization;
- callback exchange;
- token audience;
- MCP initialization and tool discovery.

This avoids treating every missing tool as a generic connection failure.

## Release Flow

1. Update shared skills and synchronized manifests.
2. Run automated cross-host validation.
3. Build and inspect the ChatGPT artifact.
4. Validate and smoke-test Claude.
5. Run live ChatGPT OAuth and MCP smoke tests.
6. Complete submission metadata, assets, domain verification, and reviewer
   access in the OpenAI submission flow.
7. Submit for public review.

## Success Criteria

- The ChatGPT archive passes automated package validation.
- The Claude plugin passes strict validation without losing its MCP header or
  SessionStart behavior.
- Shared skills are useful and host-neutral.
- ChatGPT OAuth uses `public-mcp-client` without a secret.
- ChatGPT can discover required tools without the Claude-only toolset header.
- Repository review materials satisfy the public-submission checklist without
  containing secrets.
- Live read and write smoke tests pass in both supported hosts.
