#!/usr/bin/env python3
"""Validate the portable and Claude-compatible plugin package contract."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
EXPECTED_CHATGPT_MCP_SCHEMA = (
    "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
)
EXPECTED_CLAUDE_MCP_SERVER = {
    "type": "http",
    "url": "https://mcp.cloudbees.io/v1/mcp",
    "headers": {"X-MCP-Toolsets": "all"},
    "oauth": {"clientId": "public-mcp-client"},
}
EXPECTED_CHATGPT_MCP_SERVER = {
    "type": "streamable-http",
    "url": "https://mcp.cloudbees.io/v1/mcp",
    "extensions": {
        "com.openai": {
            "auth": {
                "type": "oauth",
                "client": {
                    "mode": "provided",
                    "clientId": "public-mcp-client",
                    "tokenEndpointAuthMethod": "none",
                },
            }
        }
    },
}


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise ValueError(f"Missing required file: {relative_path}") from None
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {relative_path}: {error.msg}") from None


def validate() -> list[str]:
    errors = []
    portable_manifest = load_json("plugin.json")
    claude_manifest = load_json(".claude-plugin/plugin.json")
    marketplace_manifest = load_json(".claude-plugin/marketplace.json")
    chatgpt_mcp = load_json("mcp.json")
    claude_mcp = load_json(".mcp.json")

    if portable_manifest.get("$schema") != EXPECTED_SCHEMA:
        errors.append("plugin.json must declare the Agent Plugins 1.0.0 schema.")

    versions = {
        "plugin.json": portable_manifest.get("version"),
        ".claude-plugin/plugin.json": claude_manifest.get("version"),
        ".claude-plugin/marketplace.json": (
            marketplace_manifest.get("plugins", [{}])[0].get("version")
        ),
    }
    if len(set(versions.values())) != 1 or None in versions.values():
        errors.append(f"Manifest versions must match: {versions}.")

    if portable_manifest.get("name") != claude_manifest.get("name"):
        errors.append("Portable and Claude plugin manifests must use the same name.")

    if not isinstance(portable_manifest.get("repository"), str):
        errors.append("plugin.json repository must be a source repository URL string.")

    interface = (
        portable_manifest.get("extensions", {})
        .get("com.openai", {})
        .get("interface", {})
    )
    required_interface_fields = {
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "websiteURL",
        "supportURL",
        "privacyPolicyURL",
        "termsOfServiceURL",
        "defaultPrompt",
    }
    if not required_interface_fields.issubset(interface):
        errors.append("plugin.json must include the required OpenAI listing metadata.")
    if len(interface.get("shortDescription", "")) > 30:
        errors.append("OpenAI shortDescription must be 30 characters or fewer.")

    if chatgpt_mcp.get("$schema") != EXPECTED_CHATGPT_MCP_SCHEMA:
        errors.append("mcp.json must declare the OpenAI MCP schema.")

    chatgpt_server = chatgpt_mcp.get("mcpServers", {}).get("unify-mcp-server")
    if chatgpt_server != EXPECTED_CHATGPT_MCP_SERVER:
        errors.append(
            "ChatGPT MCP config must use streamable HTTP and public-mcp-client "
            "as a provided public OAuth client with no headers or secret."
        )

    claude_server = claude_mcp.get("mcpServers", {}).get("unify-mcp-server")
    if claude_server != EXPECTED_CLAUDE_MCP_SERVER:
        errors.append(
            "Claude MCP config must retain the expected HTTP URL, toolset "
            "header, and public OAuth client ID."
        )

    return errors


def main() -> int:
    try:
        errors = validate()
    except ValueError as error:
        print(f"Plugin layout validation failed: {error}", file=sys.stderr)
        return 1

    if errors:
        print("Plugin layout validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Plugin layout validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
