import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PluginLayoutTest(unittest.TestCase):
    def load_json(self, relative_path):
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), f"Missing required file: {relative_path}")
        return json.loads(path.read_text())

    def test_chatgpt_mcp_uses_provided_public_oauth_client(self):
        chatgpt_mcp = self.load_json("mcp.json")
        self.assertEqual(
            chatgpt_mcp["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        )
        server = chatgpt_mcp["mcpServers"]["unify-mcp-server"]

        self.assertEqual(server["type"], "streamable-http")
        self.assertEqual(server["url"], "https://mcp.cloudbees.io/v1/mcp")
        self.assertNotIn("headers", server)

        auth = server["extensions"]["com.openai"]["auth"]
        self.assertEqual(auth["type"], "oauth")
        self.assertEqual(auth["client"]["mode"], "provided")
        self.assertEqual(auth["client"]["clientId"], "public-mcp-client")
        self.assertEqual(auth["client"]["tokenEndpointAuthMethod"], "none")
        self.assertNotIn("clientSecret", auth["client"])

    def test_chatgpt_manifest_has_public_listing_metadata(self):
        manifest = self.load_json("plugin.json")
        self.assertIn("extensions", manifest)
        self.assertIn("ChatGPT", manifest["description"])
        self.assertEqual(
            manifest["repository"],
            "https://github.com/cloudbees-oss/cloudbees-unify-ai-plugin",
        )
        interface = manifest["extensions"]["com.openai"]["interface"]

        self.assertEqual(interface["displayName"], "CloudBees Unify")
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertTrue(interface["longDescription"])
        self.assertEqual(interface["developerName"], "CloudBees")
        self.assertEqual(interface["category"], "Developer Tools")
        self.assertEqual(interface["websiteURL"], "https://www.cloudbees.com/unify")
        self.assertEqual(interface["supportURL"], "https://support.cloudbees.com/")
        self.assertEqual(
            interface["privacyPolicyURL"],
            "https://www.cloudbees.com/legal/privacy-policy",
        )
        self.assertEqual(
            interface["termsOfServiceURL"],
            "https://www.cloudbees.com/company/terms-of-service",
        )
        self.assertEqual(len(interface["defaultPrompt"]), 3)

    def test_claude_mcp_contract_remains_unchanged(self):
        claude_mcp = self.load_json(".mcp.json")
        server = claude_mcp["mcpServers"]["unify-mcp-server"]

        self.assertEqual(server["type"], "http")
        self.assertEqual(server["url"], "https://mcp.cloudbees.io/v1/mcp")
        self.assertEqual(server["headers"], {"X-MCP-Toolsets": "all"})
        self.assertEqual(server["oauth"], {"clientId": "public-mcp-client"})

    def test_chatgpt_package_excludes_claude_only_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "cloudbees-unify-chatgpt.zip"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_chatgpt_plugin.py",
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output_path) as archive:
                names = set(archive.namelist())

        self.assertIn("plugin.json", names)
        self.assertIn("mcp.json", names)
        self.assertIn("skills/list-components/SKILL.md", names)
        self.assertIn("skills/onboard-repo-to-unify/SKILL.md", names)
        self.assertFalse(any(name.startswith("hooks/") for name in names))
        self.assertFalse(any(name.startswith(".claude-plugin/") for name in names))
        self.assertNotIn(".mcp.json", names)

    def test_shared_skills_are_host_neutral(self):
        skill_text = "\n".join(
            path.read_text() for path in sorted((ROOT / "skills").glob("*/SKILL.md"))
        )

        self.assertNotIn("CLAUDE_PLUGIN_ROOT", skill_text)
        self.assertNotIn("/reload-plugins", skill_text)
        self.assertNotIn("check `/mcp`", skill_text)
        self.assertIn("If local repository tools are available", skill_text)
        self.assertIn("Otherwise, ask the user for the repository URL", skill_text)

    def test_openai_skill_metadata_declares_unify_dependency(self):
        expected_dependency = (
            "dependencies:\n"
            "  tools:\n"
            "    - type: mcp\n"
            "      value: unify-mcp-server\n"
            "      description: Access CloudBees Unify.\n"
            "      transport: streamable_http\n"
            "      url: https://mcp.cloudbees.io/v1/mcp\n"
        )

        for skill_name in ("list-components", "onboard-repo-to-unify"):
            with self.subTest(skill=skill_name):
                metadata_path = (
                    ROOT / "skills" / skill_name / "agents" / "openai.yaml"
                )
                self.assertTrue(
                    metadata_path.is_file(),
                    f"Missing OpenAI metadata for {skill_name}",
                )
                self.assertIn(expected_dependency, metadata_path.read_text())

    def test_validator_accepts_the_plugin_layout(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_plugin_layout.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Plugin layout validation passed.\n")


if __name__ == "__main__":
    unittest.main()
