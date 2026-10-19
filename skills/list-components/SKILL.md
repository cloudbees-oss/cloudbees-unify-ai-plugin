---
name: list-components
description: Use when the user asks what CloudBees Unify components or services they have, or needs a component name or ID for another operation.
allowed-tools:
  - mcp__unify-mcp-server__*
  - Read
  - Grep
---

# List Components

List components in a CloudBees Unify organization via the Unify MCP server.

## Inputs

- `organization` (optional) — Unify organization name or ID. If omitted, list components from the user's default organization.
- `filter` (optional) — substring to filter component names by.

## Steps

1. Call the `unify-mcp-server` component-listing tool. Pass the organization if provided.
2. If `filter` is set, narrow results client-side (case-insensitive substring match on name).
3. Render results as a markdown table: `Name | ID | Repository | Last activity`.
4. If zero components are returned, say so explicitly. Don't fabricate placeholder rows.

## Notes

- First call may trigger OAuth in the browser. Tell the user this is expected.
- If the MCP server is disconnected or unauthenticated, tell the user to reconnect
  the Unify integration in their current host and complete the browser OAuth flow,
  then retry.
- Component IDs are the right input for downstream skills (build status, workflow runs). Prefer IDs over names when chaining.
