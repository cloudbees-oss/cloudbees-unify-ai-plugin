# ChatGPT Plugin Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a ChatGPT-compatible plugin package that uses `public-mcp-client` as a public OAuth client while preserving the existing Claude Code package and lifecycle hook.

**Architecture:** Keep shared skills in `skills/`, retain Claude-specific manifests and hooks, and add a separate OpenAI-format root `mcp.json`. Build the public ChatGPT ZIP from an explicit allowlist so Claude hooks and manifests cannot leak into the submission artifact.

**Tech Stack:** JSON, YAML, Markdown, Python 3 standard library, `unittest`, Claude plugin validator.

---

### Task 1: Specify the dual-host manifest contract

**Files:**
- Modify: `tests/test_plugin_layout.py`
- Modify: `scripts/validate_plugin_layout.py`
- Create: `mcp.json`
- Verify: `.mcp.json`
- Verify: `plugin.json`

- [ ] **Step 1: Write failing tests for the ChatGPT MCP contract**

Add tests that load `mcp.json` and assert:

```python
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
```

Retain separate assertions for the Claude `.mcp.json` contract, including its
`X-MCP-Toolsets: all` header and `oauth.clientId`.

- [ ] **Step 2: Run the tests to verify RED**

Run:

```bash
python3 -m unittest tests.test_plugin_layout -v
```

Expected: FAIL because `mcp.json` does not exist.

- [ ] **Step 3: Add the ChatGPT MCP manifest**

Create `mcp.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "unify-mcp-server": {
      "type": "streamable-http",
      "url": "https://mcp.cloudbees.io/v1/mcp",
      "extensions": {
        "com.openai": {
          "auth": {
            "type": "oauth",
            "client": {
              "mode": "provided",
              "clientId": "public-mcp-client",
              "tokenEndpointAuthMethod": "none"
            }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Update the validator for separate host contracts**

Replace the equality check between `mcp.json` and `.mcp.json` with independent
validation. Add explicit errors for:

- wrong ChatGPT transport
- ChatGPT static headers
- wrong OAuth mode, client ID, or token endpoint auth method
- any ChatGPT client secret
- changed Claude URL, header, or public client ID

- [ ] **Step 5: Run the tests to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_plugin_layout -v
python3 scripts/validate_plugin_layout.py
```

Expected: all tests pass and the validator prints
`Plugin layout validation passed.`

### Task 2: Add a safe ChatGPT packaging boundary

**Files:**
- Modify: `tests/test_plugin_layout.py`
- Create: `scripts/build_chatgpt_plugin.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write a failing package-content test**

Add a test that runs the builder into a temporary directory and checks:

```python
with zipfile.ZipFile(output_path) as archive:
    names = set(archive.namelist())

self.assertIn("plugin.json", names)
self.assertIn("mcp.json", names)
self.assertIn("skills/list-components/SKILL.md", names)
self.assertIn("skills/onboard-repo-to-unify/SKILL.md", names)
self.assertFalse(any(name.startswith("hooks/") for name in names))
self.assertFalse(any(name.startswith(".claude-plugin/") for name in names))
self.assertNotIn(".mcp.json", names)
```

- [ ] **Step 2: Run the package test to verify RED**

Run:

```bash
python3 -m unittest tests.test_plugin_layout.PluginLayoutTest.test_chatgpt_package_excludes_claude_only_files -v
```

Expected: FAIL because `scripts/build_chatgpt_plugin.py` does not exist.

- [ ] **Step 3: Implement the allowlist-based ZIP builder**

Create a Python script using `argparse`, `pathlib`, and `zipfile`. Include only:

```python
ROOT_FILES = ("plugin.json", "mcp.json", "README.md", "LICENSE")
SKILL_FILE_NAMES = ("SKILL.md", "openai.yaml")
```

Include `openai.yaml` only when it is under a skill’s `agents/` directory.
Default the output to `dist/cloudbees-unify-chatgpt.zip`, and accept
`--output PATH` for tests.

- [ ] **Step 4: Ignore generated ZIP artifacts**

Ensure `.gitignore` contains:

```gitignore
dist/
```

It already does, so make no change unless the test reveals otherwise.

- [ ] **Step 5: Run the package test to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_plugin_layout.PluginLayoutTest.test_chatgpt_package_excludes_claude_only_files -v
```

Expected: PASS.

### Task 3: Make shared skills portable and discoverable

**Files:**
- Modify: `tests/test_plugin_layout.py`
- Modify: `skills/list-components/SKILL.md`
- Modify: `skills/onboard-repo-to-unify/SKILL.md`
- Create: `skills/list-components/agents/openai.yaml`
- Create: `skills/onboard-repo-to-unify/agents/openai.yaml`

- [ ] **Step 1: Write failing portability tests**

Assert that shared skills do not contain `CLAUDE_PLUGIN_ROOT`, `/reload-plugins`,
or a recovery instruction that requires `/mcp`. Assert both OpenAI metadata
files exist and contain:

```yaml
dependencies:
  tools:
    - type: mcp
      value: unify-mcp-server
      description: Access CloudBees Unify.
      transport: streamable_http
      url: https://mcp.cloudbees.io/v1/mcp
```

- [ ] **Step 2: Run the portability tests to verify RED**

Run:

```bash
python3 -m unittest tests.test_plugin_layout.PluginLayoutTest.test_shared_skills_are_host_neutral -v
python3 -m unittest tests.test_plugin_layout.PluginLayoutTest.test_openai_skill_metadata_declares_unify_dependency -v
```

Expected: FAIL because the onboarding skill contains Claude commands and the
metadata files do not exist.

- [ ] **Step 3: Rewrite host-specific skill guidance**

Change connection recovery to:

```markdown
If the call fails because the MCP server is disconnected or unauthenticated,
tell the user to reconnect the Unify integration in their current host and
complete the browser OAuth flow, then retry.
```

Change repository discovery to:

```markdown
If local repository tools are available, obtain the origin URL and default
branch with Git. Otherwise, ask the user for the repository URL and default
branch.
```

Keep Claude `allowed-tools` frontmatter intact.

- [ ] **Step 4: Add OpenAI skill metadata**

Create metadata with a concise `interface` section, a default prompt, and the
Unify MCP dependency shown above. Do not add icon paths until publication assets
exist.

- [ ] **Step 5: Run the portability tests to verify GREEN**

Run:

```bash
python3 -m unittest tests.test_plugin_layout -v
```

Expected: all tests pass.

### Task 4: Document installation, compatibility, and server prerequisites

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `SECURITY.md`

- [ ] **Step 1: Add a host compatibility table**

Document:

| Host | Manifest | MCP config | Hooks |
| --- | --- | --- | --- |
| ChatGPT | `plugin.json` | `mcp.json` | Excluded |
| Claude Code | `.claude-plugin/plugin.json` | `.mcp.json` | Included |
| Cursor/VS Code/Copilot CLI | Portable or Claude-compatible package as supported | Host-specific discovery | No ChatGPT guarantee |

- [ ] **Step 2: Document ChatGPT build and private-test commands**

Add:

```bash
python3 scripts/validate_plugin_layout.py
python3 scripts/build_chatgpt_plugin.py
```

State that private connectivity should first be tested by adding
`https://mcp.cloudbees.io/v1/mcp` as a custom MCP connection.

- [ ] **Step 3: Document external server prerequisites**

State explicitly that:

- `public-mcp-client` is a public OAuth client with no secret
- ChatGPT uses token endpoint authentication method `none`
- the server must expose the required tools without
  `X-MCP-Toolsets: all`
- OAuth discovery, callback registration, tool annotations, and live auth must
  be smoke-tested against the deployed server

- [ ] **Step 4: Document contribution and release checks**

Explain synchronized manifest versions, separate MCP contracts, generated ZIP
contents, and Claude validation.

- [ ] **Step 5: Run documentation checks**

Run:

```bash
rg -n "ChatGPT|public-mcp-client|streamable-http|SessionStart|build_chatgpt_plugin" README.md CONTRIBUTING.md SECURITY.md
```

Expected: every compatibility and release concept appears.

### Task 5: Final verification

**Files:**
- Verify all modified files

- [ ] **Step 1: Run the full automated suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_plugin_layout.py
```

Expected: zero failures and successful layout validation.

- [ ] **Step 2: Build and inspect the ChatGPT artifact**

Run:

```bash
python3 scripts/build_chatgpt_plugin.py
unzip -l dist/cloudbees-unify-chatgpt.zip
```

Expected: portable manifests and skills are present; Claude manifests and hooks
are absent.

- [ ] **Step 3: Revalidate Claude support**

Run:

```bash
claude plugin validate . --strict
```

Expected: validation passes.

- [ ] **Step 4: Check repository hygiene**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors; existing unrelated untracked work remains
untouched.

- [ ] **Step 5: Record manual follow-up**

Report that live ChatGPT OAuth and headerless tool discovery still require a
network-accessible smoke test against `mcp.cloudbees.io`.
