# Security Policy

## Reporting a vulnerability

If you discover a security issue in this plugin, please report it privately to the CloudBees security team rather than filing a public issue. See https://www.cloudbees.com/security for current contact details.

## Scope

This plugin is a thin wrapper that routes requests through the CloudBees Unify
MCP server (`https://mcp.cloudbees.io/v1/mcp`). Authentication is handled by
Unify's OAuth flow, and credentials are stored by the MCP host rather than this
plugin.

ChatGPT uses `public-mcp-client` as a public OAuth client with token endpoint
authentication method `none`. The package must never contain a client secret.
Claude Code continues to use the same public client through `.mcp.json`.
