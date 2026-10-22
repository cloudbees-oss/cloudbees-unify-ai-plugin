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

1. Resolve the organization ID:
   - If `organization` is a UUID, use it directly.
   - If it's omitted, call `user_whoami` and use its `selected_organization` as the name. If that field is missing, ask the user for the organization.
   - Call `organizations_list` with `name` set to the name. Pass a plain fragment, not a wildcard pattern; it matches display name or domain name, case-insensitively.
   - One match: use its `id`.
   - Several matches: list each `displayName`, `domainName`, and `id`, and ask the user which one to use.
   - No match: sub-organizations aren't returned by a name search. Call `organizations_list` with `nested: true` and no `name`, and look for the name in `childOrganizations` at every depth (without `nested: true`, most sub-organizations are left out). If it's still not found, say so and ask the user. Don't guess.
2. Call `services_list` with `organizationId` and `typeFilter: COMPONENT_FILTER`. It returns every component in one `items` array (no pagination), including components in the organization's sub-organizations.
3. If `filter` is set, narrow results client-side (case-insensitive substring match on name). The tool has no name filter.
4. Render results as a markdown table: `Name | ID | Repository`, using `repositoryUrl` for the repository. If there are more than 50 rows, give the total count and ask the user for a `filter` before printing the full table.
5. If zero components are returned, say so explicitly. Don't fabricate placeholder rows.

## Notes

- First call may trigger OAuth in the browser. Tell the user this is expected.
- Component IDs are the right input for downstream skills (build status, workflow runs). Prefer IDs over names when chaining.
