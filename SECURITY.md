# Security Policy

## Reporting a vulnerability

If you discover a security issue in this plugin, please report it privately to the CloudBees security team rather than filing a public issue. See https://www.cloudbees.com/security for current contact details.

## Scope

This plugin is a thin wrapper that routes requests through the CloudBees Unify MCP server (`https://mcp.cloudbees.io/v1/mcp`). Authentication is handled by Unify's OAuth flow — credentials are stored by the MCP client (Claude Code or GitHub Copilot CLI), not by this plugin. The plugin itself does not handle secrets.
