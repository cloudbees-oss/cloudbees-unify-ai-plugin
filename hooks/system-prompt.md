# CloudBees Unify Plugin

The `cloudbees-unify` plugin is loaded. The user can talk to CloudBees Unify (components, workflows, builds, security findings, feature flags) through the `unify-mcp-server` MCP server.

When a user asks about Unify resources, prefer the skills under `skills/`. The MCP server handles auth via browser OAuth on first use — tell the user to expect a browser prompt the first time.

Do not fabricate Unify data. If the MCP server isn't connected, say so.
