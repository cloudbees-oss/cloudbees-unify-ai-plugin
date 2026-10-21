---
name: list-components
description: List CloudBees Unify components in an organization. Use when the user asks "what components do I have", "list services", or needs to look up a component name/ID before another operation.
allowed-tools:
  - mcp__unify-mcp-server__*
  - mcp__plugin_cloudbees-unify_unify-mcp-server__*
  - Read
  - Grep
---

# List Components

List components in a CloudBees Unify organization via the Unify MCP server.

## Inputs

- `organization` (optional) — Unify organization name or ID. If omitted, list components from the user's default organization.
- `filter` (optional) — substring to filter component names by.

## Steps

1. If `organization` is a name, resolve it to an ID with `organizations_search`.
2. Call `services_list` with the organization ID and `typeFilter: COMPONENT_FILTER`.
3. If `filter` is set, narrow results client-side (case-insensitive substring match on name). The tool has no name filter.
4. Render results as a markdown table: `Name | ID | Repository`, using `repositoryUrl` for the repository.
5. If zero components are returned, say so explicitly. Don't fabricate placeholder rows.

## Notes

- First call may trigger OAuth in the browser. Tell the user this is expected.
- Component IDs are the right input for downstream skills (build status, workflow runs). Prefer IDs over names when chaining.
