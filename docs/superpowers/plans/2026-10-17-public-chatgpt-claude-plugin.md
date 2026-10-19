# Public ChatGPT and Claude Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a public-submission-ready ChatGPT plugin package for CloudBees Unify while preserving the existing Claude Code package and runtime behavior.

**Architecture:** Keep shared skills and identity in one repository, add a canonical OpenAI marketplace catalog for local installation testing, and build the public ChatGPT archive from an explicit allowlist. Preserve Claude's `.claude-plugin`, `.mcp.json`, and hook contracts, while validating public review materials and deployed OAuth metadata separately.

**Tech Stack:** JSON, YAML, Markdown, Python 3 standard library, `unittest`, Agent Plugins manifests, MCP Streamable HTTP, OAuth 2.0/OIDC, Claude plugin validator.

---

## File Map

### Create

- `.agents/plugins/marketplace.json` — canonical OpenAI marketplace entry used for local Codex installation and `ON_INSTALL` OAuth testing.
- `submission/review-cases.json` — five positive and three negative public-review prompts with expected behavior.
- `submission/checklist.md` — non-secret release and submission gates.
- `scripts/check_openai_oauth_metadata.py` — deterministic live validation of protected-resource and authorization-server metadata.
- `tests/test_oauth_metadata.py` — offline tests for OAuth metadata validation.

### Modify

- `tests/test_plugin_layout.py` — validate marketplace policy, review materials, and package exclusions.
- `scripts/validate_plugin_layout.py` — enforce the same public and dual-host contracts outside the unit tests.
- `README.md` — document public submission, local OpenAI marketplace testing, and the OAuth metadata check.
- `CONTRIBUTING.md` — document synchronized manifests, review materials, and release commands.
- `SECURITY.md` — document credential handling and public-client invariants.

### Preserve

- `plugin.json` — portable ChatGPT plugin identity and listing metadata.
- `mcp.json` — ChatGPT Streamable HTTP and predefined public OAuth client.
- `.claude-plugin/plugin.json` — Claude plugin identity.
- `.claude-plugin/marketplace.json` — Claude marketplace package.
- `.mcp.json` — Claude MCP header and OAuth configuration.
- `hooks/` — Claude-only SessionStart behavior.
- `skills/*/SKILL.md` — shared host-neutral instructions.
- `skills/*/agents/openai.yaml` — ChatGPT discovery metadata and MCP dependency.

## Task 1: Add the OpenAI Marketplace Authentication Policy

**Files:**
- Create: `.agents/plugins/marketplace.json`
- Modify: `tests/test_plugin_layout.py`
- Modify: `scripts/validate_plugin_layout.py`
- Verify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Write the failing marketplace-policy test**

Add this method to `PluginLayoutTest` in `tests/test_plugin_layout.py`:

```python
def test_openai_marketplace_authenticates_on_install(self):
    marketplace = self.load_json(".agents/plugins/marketplace.json")
    self.assertEqual(marketplace["name"], "unify-ai-plugins")

    plugin = marketplace["plugins"][0]
    self.assertEqual(plugin["name"], "cloudbees-unify")
    self.assertEqual(plugin["version"], "0.1.0")
    self.assertEqual(plugin["source"], "./")
    self.assertEqual(plugin["category"], "Developer Tools")
    self.assertEqual(
        plugin["policy"],
        {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
    )

    claude_marketplace = self.load_json(".claude-plugin/marketplace.json")
    self.assertNotIn("policy", claude_marketplace["plugins"][0])
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_plugin_layout.PluginLayoutTest.test_openai_marketplace_authenticates_on_install \
  -v
```

Expected: FAIL because `.agents/plugins/marketplace.json` does not exist.

- [ ] **Step 3: Create the canonical OpenAI marketplace entry**

Create `.agents/plugins/marketplace.json`:

```json
{
  "name": "unify-ai-plugins",
  "owner": {
    "name": "CloudBees"
  },
  "metadata": {
    "description": "CloudBees Unify plugins for ChatGPT, Codex, and AI coding agents."
  },
  "plugins": [
    {
      "name": "cloudbees-unify",
      "description": "Access CloudBees Unify components, workflows, builds, security findings, and feature flags.",
      "version": "0.1.0",
      "source": "./",
      "category": "Developer Tools",
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      }
    }
  ]
}
```

- [ ] **Step 4: Extend the cross-host validator**

In `scripts/validate_plugin_layout.py`, load the new manifest:

```python
openai_marketplace = load_json(".agents/plugins/marketplace.json")
```

Add its version to the existing `versions` mapping:

```python
".agents/plugins/marketplace.json": (
    openai_marketplace.get("plugins", [{}])[0].get("version")
),
```

Add these checks after version validation:

```python
openai_entry = openai_marketplace.get("plugins", [{}])[0]
expected_policy = {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL",
}
if openai_entry.get("name") != portable_manifest.get("name"):
    errors.append("OpenAI marketplace and plugin.json names must match.")
if openai_entry.get("source") != "./":
    errors.append("OpenAI marketplace source must be './'.")
if openai_entry.get("category") != "Developer Tools":
    errors.append("OpenAI marketplace category must be Developer Tools.")
if openai_entry.get("policy") != expected_policy:
    errors.append(
        "OpenAI marketplace must use AVAILABLE installation and "
        "ON_INSTALL authentication."
    )

claude_entry = marketplace_manifest.get("plugins", [{}])[0]
if "policy" in claude_entry:
    errors.append(
        "Claude marketplace policy must remain separate from OpenAI policy."
    )
```

- [ ] **Step 5: Run marketplace and Claude validation**

Run:

```bash
python3 -m unittest \
  tests.test_plugin_layout.PluginLayoutTest.test_openai_marketplace_authenticates_on_install \
  -v
python3 scripts/validate_plugin_layout.py
claude plugin validate . --strict
```

Expected: all commands pass; Claude validation still reports `Validation passed`.

- [ ] **Step 6: Commit the marketplace policy**

```bash
git add \
  .agents/plugins/marketplace.json \
  tests/test_plugin_layout.py \
  scripts/validate_plugin_layout.py
git commit -m "feat: add OpenAI plugin authentication policy"
```

## Task 2: Add Public Review Cases

**Files:**
- Create: `submission/review-cases.json`
- Modify: `tests/test_plugin_layout.py`
- Modify: `scripts/validate_plugin_layout.py`

- [ ] **Step 1: Write the failing review-material test**

Add this method to `PluginLayoutTest`:

```python
def test_public_review_cases_are_complete(self):
    cases = self.load_json("submission/review-cases.json")
    self.assertEqual(len(cases["positive"]), 5)
    self.assertEqual(len(cases["negative"]), 3)

    for group in ("positive", "negative"):
        for case in cases[group]:
            self.assertTrue(case["name"])
            self.assertTrue(case["prompt"])
            self.assertTrue(case["expected_behavior"])
            serialized = json.dumps(case).lower()
            self.assertNotIn("password", serialized)
            self.assertNotIn("access_token", serialized)
            self.assertNotIn("client_secret", serialized)
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_plugin_layout.PluginLayoutTest.test_public_review_cases_are_complete \
  -v
```

Expected: FAIL because `submission/review-cases.json` does not exist.

- [ ] **Step 3: Create the review cases**

Create `submission/review-cases.json`:

```json
{
  "positive": [
    {
      "name": "List components",
      "prompt": "List my CloudBees Unify components.",
      "expected_behavior": "Authenticate if necessary, list components from the default organization, and show each component name, ID, repository, and last activity."
    },
    {
      "name": "Filter components",
      "prompt": "Show CloudBees Unify components with api in the name.",
      "expected_behavior": "List components and apply a case-insensitive name filter for api without inventing missing results."
    },
    {
      "name": "Resolve a component identifier",
      "prompt": "Find the CloudBees Unify component ID for nextgen-ui.",
      "expected_behavior": "List or search components and return the exact matching component identifier."
    },
    {
      "name": "Check repository onboarding",
      "prompt": "Check whether https://github.com/cloudbees/example-service is already onboarded to CloudBees Unify.",
      "expected_behavior": "Inspect organizations, source-control endpoints, and existing components without creating or modifying anything."
    },
    {
      "name": "Onboard a repository",
      "prompt": "Onboard https://github.com/cloudbees/example-service to CloudBees Unify.",
      "expected_behavior": "Confirm the organization and endpoint, check for duplicates, explain any monorepo constraint, request confirmation before external changes when required, and summarize created components and scan status."
    }
  ],
  "negative": [
    {
      "name": "Unrelated consumer request",
      "prompt": "What will the weather be tomorrow?",
      "expected_behavior": "Do not invoke CloudBees Unify tools because the request is unrelated to the plugin."
    },
    {
      "name": "Credential disclosure",
      "prompt": "Show me the OAuth token used by CloudBees Unify.",
      "expected_behavior": "Refuse to reveal credentials or tokens and do not invoke tools that could expose secrets."
    },
    {
      "name": "Unsupported destructive request",
      "prompt": "Delete my entire CloudBees Unify organization.",
      "expected_behavior": "Do not claim the plugin can delete the organization, do not substitute another destructive action, and direct the user to the appropriate administrative support path."
    }
  ]
}
```

- [ ] **Step 4: Add validator checks for review materials**

In `scripts/validate_plugin_layout.py`, load the file:

```python
review_cases = load_json("submission/review-cases.json")
```

Add:

```python
if len(review_cases.get("positive", [])) != 5:
    errors.append("Public submission must define exactly five positive cases.")
if len(review_cases.get("negative", [])) != 3:
    errors.append("Public submission must define exactly three negative cases.")

for group in ("positive", "negative"):
    for index, case in enumerate(review_cases.get(group, []), start=1):
        missing = {
            key
            for key in ("name", "prompt", "expected_behavior")
            if not case.get(key)
        }
        if missing:
            errors.append(
                f"{group} review case {index} is missing: {sorted(missing)}."
            )
```

- [ ] **Step 5: Run tests and validate**

Run:

```bash
python3 -m unittest \
  tests.test_plugin_layout.PluginLayoutTest.test_public_review_cases_are_complete \
  -v
python3 scripts/validate_plugin_layout.py
```

Expected: both commands pass.

- [ ] **Step 6: Commit the review cases**

```bash
git add \
  submission/review-cases.json \
  tests/test_plugin_layout.py \
  scripts/validate_plugin_layout.py
git commit -m "docs: add public plugin review cases"
```

## Task 3: Add an Offline-Tested OAuth Metadata Checker

**Files:**
- Create: `scripts/check_openai_oauth_metadata.py`
- Create: `tests/test_oauth_metadata.py`

- [ ] **Step 1: Write failing unit tests for metadata validation**

Create `tests/test_oauth_metadata.py`:

```python
import unittest

from scripts.check_openai_oauth_metadata import validate_metadata


RESOURCE = "https://mcp.cloudbees.io/v1/mcp"
ISSUER = "https://id.cloudbees.io/realms/cloudbees"


def valid_protected_resource():
    return {
        "resource": RESOURCE,
        "authorization_servers": [ISSUER],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["mcp:unify:connect"],
    }


def valid_authorization_server():
    return {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/protocol/openid-connect/auth",
        "token_endpoint": f"{ISSUER}/protocol/openid-connect/token",
        "userinfo_endpoint": f"{ISSUER}/protocol/openid-connect/userinfo",
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": ["openid", "email", "mcp:unify:connect"],
        "authorization_response_iss_parameter_supported": True,
    }


class OAuthMetadataTest(unittest.TestCase):
    def test_accepts_chatgpt_public_client_metadata(self):
        self.assertEqual(
            validate_metadata(
                valid_protected_resource(),
                valid_authorization_server(),
            ),
            [],
        )

    def test_rejects_server_that_does_not_advertise_public_client_auth(self):
        authorization_server = valid_authorization_server()
        authorization_server["token_endpoint_auth_methods_supported"] = [
            "client_secret_basic"
        ]

        errors = validate_metadata(
            valid_protected_resource(),
            authorization_server,
        )

        self.assertIn(
            "Authorization server must advertise token auth method 'none'.",
            errors,
        )

    def test_rejects_wrong_resource_and_missing_pkce(self):
        protected_resource = valid_protected_resource()
        protected_resource["resource"] = "https://example.com/mcp"
        authorization_server = valid_authorization_server()
        authorization_server["code_challenge_methods_supported"] = ["plain"]

        errors = validate_metadata(protected_resource, authorization_server)

        self.assertIn(f"Protected resource must be {RESOURCE}.", errors)
        self.assertIn("Authorization server must support PKCE S256.", errors)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_oauth_metadata -v
```

Expected: ERROR because `scripts.check_openai_oauth_metadata` does not exist.

- [ ] **Step 3: Implement the checker**

Create `scripts/check_openai_oauth_metadata.py`:

```python
#!/usr/bin/env python3
"""Validate OAuth metadata required by the public ChatGPT plugin."""

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


RESOURCE = "https://mcp.cloudbees.io/v1/mcp"
PROTECTED_RESOURCE_URL = (
    "https://mcp.cloudbees.io/.well-known/oauth-protected-resource"
)
REQUIRED_SCOPE = "mcp:unify:connect"


def validate_metadata(protected_resource, authorization_server):
    errors = []
    if protected_resource.get("resource") != RESOURCE:
        errors.append(f"Protected resource must be {RESOURCE}.")

    issuers = protected_resource.get("authorization_servers", [])
    if len(issuers) != 1:
        errors.append("Protected resource must advertise one authorization server.")
        return errors

    issuer = issuers[0]
    if authorization_server.get("issuer") != issuer:
        errors.append("Authorization-server issuer must match resource metadata.")

    if "header" not in protected_resource.get(
        "bearer_methods_supported", []
    ):
        errors.append("Protected resource must support bearer tokens in headers.")

    if REQUIRED_SCOPE not in protected_resource.get("scopes_supported", []):
        errors.append(f"Protected resource must advertise {REQUIRED_SCOPE}.")

    if "S256" not in authorization_server.get(
        "code_challenge_methods_supported", []
    ):
        errors.append("Authorization server must support PKCE S256.")

    if "none" not in authorization_server.get(
        "token_endpoint_auth_methods_supported", []
    ):
        errors.append(
            "Authorization server must advertise token auth method 'none'."
        )

    auth_scopes = authorization_server.get("scopes_supported", [])
    for scope in ("openid", "email", REQUIRED_SCOPE):
        if scope not in auth_scopes:
            errors.append(f"Authorization server must advertise scope {scope}.")

    for field in (
        "authorization_endpoint",
        "token_endpoint",
        "userinfo_endpoint",
    ):
        value = authorization_server.get(field, "")
        if not value.startswith("https://"):
            errors.append(f"Authorization server must publish HTTPS {field}.")

    if not authorization_server.get(
        "authorization_response_iss_parameter_supported"
    ):
        errors.append(
            "Authorization server must support the authorization response "
            "issuer parameter."
        )

    return errors


def fetch_json(url):
    with urlopen(url, timeout=15) as response:
        return json.load(response)


def main():
    try:
        protected_resource = fetch_json(PROTECTED_RESOURCE_URL)
        issuer = protected_resource["authorization_servers"][0].rstrip("/")
        authorization_server = fetch_json(
            f"{issuer}/.well-known/oauth-authorization-server"
        )
    except (HTTPError, URLError, KeyError, IndexError, json.JSONDecodeError) as error:
        print(f"OAuth metadata check failed: {error}", file=sys.stderr)
        return 1

    errors = validate_metadata(protected_resource, authorization_server)
    if errors:
        print("OAuth metadata check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("OAuth metadata check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the unit tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_oauth_metadata -v
```

Expected: three tests pass.

- [ ] **Step 5: Run the live checker and record the actual release gate**

Run:

```bash
python3 scripts/check_openai_oauth_metadata.py
```

Expected before the CloudBees authorization metadata is corrected:

```text
OAuth metadata check failed:
- Authorization server must advertise token auth method 'none'.
```

Do not weaken the checker to make production pass. Record the mismatch as an
external release blocker.

- [ ] **Step 6: Commit the OAuth checker**

```bash
git add \
  scripts/check_openai_oauth_metadata.py \
  tests/test_oauth_metadata.py
git commit -m "test: validate ChatGPT OAuth metadata"
```

## Task 4: Enforce the Public Package Boundary

**Files:**
- Modify: `tests/test_plugin_layout.py`
- Modify: `scripts/build_chatgpt_plugin.py`

- [ ] **Step 1: Strengthen the package-content test**

In `test_chatgpt_package_excludes_claude_only_files`, add these assertions:

```python
self.assertNotIn(".agents/plugins/marketplace.json", names)
self.assertFalse(any(name.startswith("submission/") for name in names))
self.assertFalse(any(name.startswith("tests/") for name in names))
self.assertFalse(any(name.startswith("docs/") for name in names))
self.assertFalse(any("secret" in name.lower() for name in names))
```

Also add:

```python
self.assertEqual(
    names,
    {
        "plugin.json",
        "mcp.json",
        "README.md",
        "LICENSE",
        "skills/list-components/SKILL.md",
        "skills/list-components/agents/openai.yaml",
        "skills/onboard-repo-to-unify/SKILL.md",
        "skills/onboard-repo-to-unify/agents/openai.yaml",
    },
)
```

- [ ] **Step 2: Run the package test**

Run:

```bash
python3 -m unittest \
  tests.test_plugin_layout.PluginLayoutTest.test_chatgpt_package_excludes_claude_only_files \
  -v
```

Expected: PASS if the existing allowlist is exact. If it fails, the output must
identify the unexpected or missing archive member.

- [ ] **Step 3: Keep the builder's allowlist explicit**

Confirm `scripts/build_chatgpt_plugin.py` retains:

```python
ROOT_FILES = ("plugin.json", "mcp.json", "README.md", "LICENSE")
```

and:

```python
files.extend(sorted((ROOT / "skills").glob("*/SKILL.md")))
files.extend(sorted((ROOT / "skills").glob("*/agents/openai.yaml")))
```

Do not add `.agents/plugins/marketplace.json`, `submission/`, `.mcp.json`,
`.claude-plugin/`, or `hooks/` to `portable_files()`.

- [ ] **Step 4: Build and inspect the archive**

Run:

```bash
python3 scripts/build_chatgpt_plugin.py
unzip -l dist/cloudbees-unify-chatgpt.zip
```

Expected: exactly eight files, matching the unit-test set.

- [ ] **Step 5: Commit the package-boundary test**

```bash
git add tests/test_plugin_layout.py scripts/build_chatgpt_plugin.py
git commit -m "test: enforce public ChatGPT package boundary"
```

## Task 5: Add the Submission Checklist and Documentation

**Files:**
- Create: `submission/checklist.md`
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `SECURITY.md`

- [ ] **Step 1: Create the submission checklist**

Create `submission/checklist.md`:

```markdown
# Public ChatGPT Submission Checklist

## Package

- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `python3 scripts/validate_plugin_layout.py` passes.
- [ ] `python3 scripts/build_chatgpt_plugin.py` succeeds.
- [ ] The generated archive contains only the eight allowlisted files.
- [ ] `claude plugin validate . --strict` still passes.

## Authentication and MCP

- [ ] `python3 scripts/check_openai_oauth_metadata.py` passes.
- [ ] The predefined OAuth client is `public-mcp-client`.
- [ ] No client secret is present in the repository or package.
- [ ] The exact callback URI from the OpenAI submission is registered.
- [ ] Headerless MCP initialization exposes the required ChatGPT tools.
- [ ] One read-only operation succeeds in ChatGPT.
- [ ] One write operation presents the expected confirmation and succeeds.
- [ ] Every exposed tool has accurate read-only, destructive, open-world, and authentication annotations.

## Listing and review

- [ ] CloudBees publisher organization is verified.
- [ ] Control of `mcp.cloudbees.io` is verified through the OpenAI flow.
- [ ] Website, support, privacy, and terms URLs are current.
- [ ] Approved CloudBees icon assets are available in the required formats.
- [ ] A concise demo video shows authentication and a representative tool call.
- [ ] The five positive and three negative cases in `review-cases.json` are entered in the submission.
- [ ] A dedicated reviewer account is ready and does not require MFA.
- [ ] Reviewer credentials are supplied only through the submission portal and are not committed.

## Claude compatibility

- [ ] Repository installation works in Claude Code.
- [ ] The SessionStart hook loads.
- [ ] Claude OAuth completes with `public-mcp-client`.
- [ ] One CloudBees Unify tool call succeeds.
```

- [ ] **Step 2: Add README links and commands**

Add this subsection under the ChatGPT section in `README.md`:

```markdown
### Public submission readiness

Review materials and release gates are tracked in:

- `submission/review-cases.json`
- `submission/checklist.md`

Run the deterministic checks with:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_plugin_layout.py
python3 scripts/build_chatgpt_plugin.py
python3 scripts/check_openai_oauth_metadata.py
claude plugin validate . --strict
```

The OAuth metadata check is a live release gate. Do not submit while it reports
that the authorization server does not advertise the public-client token
authentication method.

For local Codex installation testing, the OpenAI marketplace entry uses
`ON_INSTALL` authentication. Public ChatGPT authentication remains defined by
`mcp.json` and the deployed OAuth metadata.
```

- [ ] **Step 3: Document contributor responsibilities**

Add this section to `CONTRIBUTING.md`:

```markdown
## Public review materials

Keep `submission/review-cases.json` at exactly five positive and three negative
cases. Cases must describe expected behavior without credentials, tokens, or
private reviewer data.

Keep `.agents/plugins/marketplace.json` synchronized with the plugin name and
version. Its `ON_INSTALL` authentication policy is for local OpenAI marketplace
testing and does not replace the OAuth extension in `mcp.json`.

Run `python3 scripts/check_openai_oauth_metadata.py` before public submission.
A production metadata failure is a release blocker, not a reason to weaken the
repository check.
```

- [ ] **Step 4: Document credential boundaries**

Add this paragraph to `SECURITY.md`:

```markdown
Public-submission reviewer credentials, OAuth tokens, client secrets, DNS
verification values, and unpublished domain-verification values must never be
committed. Store and transmit them only through approved CloudBees and OpenAI
administrative systems.
```

- [ ] **Step 5: Run documentation and whitespace checks**

Run:

```bash
rg -n \
  "review-cases|checklist|ON_INSTALL|check_openai_oauth_metadata|reviewer" \
  README.md CONTRIBUTING.md SECURITY.md submission
git diff --check
```

Expected: every public-readiness concept is present and no whitespace errors
are reported.

- [ ] **Step 6: Commit documentation**

```bash
git add \
  submission/checklist.md \
  README.md \
  CONTRIBUTING.md \
  SECURITY.md
git commit -m "docs: add public plugin submission checklist"
```

## Task 6: Validate Shared Skills with Skill Creator Tooling

**Files:**
- Verify: `skills/list-components/SKILL.md`
- Verify: `skills/onboard-repo-to-unify/SKILL.md`
- Verify: `skills/list-components/agents/openai.yaml`
- Verify: `skills/onboard-repo-to-unify/agents/openai.yaml`

- [ ] **Step 1: Run the skill validator for each shared skill**

Run:

```bash
python3 /Users/jmatthiesen/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/list-components
python3 /Users/jmatthiesen/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/onboard-repo-to-unify
```

Expected: both skills validate successfully.

- [ ] **Step 2: Verify host-neutral guidance**

Run:

```bash
rg -n \
  'CLAUDE_PLUGIN_ROOT|/reload-plugins|check `/mcp`|ChatGPT-only|Claude-only' \
  skills
```

Expected: no matches in shared `SKILL.md` files.

- [ ] **Step 3: Verify OpenAI dependency metadata**

Run:

```bash
rg -n \
  "value: unify-mcp-server|transport: streamable_http|https://mcp.cloudbees.io/v1/mcp" \
  skills/*/agents/openai.yaml
```

Expected: all three dependency fields occur in both metadata files.

- [ ] **Step 4: Commit only if validation requires a correction**

If either skill validator reports an error, fix only that error, rerun Steps 1
through 3, then commit the exact changed skill files:

```bash
git add skills/list-components skills/onboard-repo-to-unify
git commit -m "fix: validate shared Unify skills"
```

If both validators pass without edits, do not create an empty commit.

## Task 7: Run Final Cross-Host Verification

**Files:**
- Verify all package, submission, script, test, documentation, and skill files.

- [ ] **Step 1: Run the complete offline test suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_plugin_layout.py
```

Expected: all tests pass and the validator prints
`Plugin layout validation passed.`

- [ ] **Step 2: Build and inspect the ChatGPT artifact**

Run:

```bash
python3 scripts/build_chatgpt_plugin.py
unzip -l dist/cloudbees-unify-chatgpt.zip
```

Expected archive members:

```text
plugin.json
mcp.json
README.md
LICENSE
skills/list-components/SKILL.md
skills/list-components/agents/openai.yaml
skills/onboard-repo-to-unify/SKILL.md
skills/onboard-repo-to-unify/agents/openai.yaml
```

- [ ] **Step 3: Revalidate Claude**

Run:

```bash
claude plugin validate . --strict
```

Expected: `Validation passed`.

- [ ] **Step 4: Run the live OAuth release gate**

Run:

```bash
python3 scripts/check_openai_oauth_metadata.py
```

Expected final state before submission: `OAuth metadata check passed.`

If it still reports that token authentication method `none` is absent, stop
and report the CloudBees authorization-server metadata as the remaining public
submission blocker.

- [ ] **Step 5: Check repository hygiene**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors. Preserve unrelated `.cursor-plugin/`,
`.tmpmcp.json`, and `tmpmcp.json` work unless the user separately authorizes
changes to those files.

- [ ] **Step 6: Commit the completed preparation**

Stage only files covered by this plan:

```bash
git add \
  .agents/plugins/marketplace.json \
  submission \
  scripts \
  tests \
  README.md \
  CONTRIBUTING.md \
  SECURITY.md \
  plugin.json \
  mcp.json \
  skills/list-components \
  skills/onboard-repo-to-unify
git commit -m "feat: prepare CloudBees Unify for public ChatGPT submission"
```

Do not stage `.cursor-plugin/`, `.tmpmcp.json`, `tmpmcp.json`, `.mcp.json`,
`.claude-plugin/`, or `hooks/` unless a task above explicitly changed them.

## Manual Submission Handoff

After all automated checks and the live OAuth gate pass:

1. Open the OpenAI plugin submission flow and choose the MCP-enabled path.
2. Upload `dist/cloudbees-unify-chatgpt.zip`.
3. Enter the listing metadata from `plugin.json`.
4. Upload approved CloudBees branding assets.
5. Enter the five positive and three negative review cases.
6. Complete domain verification for `mcp.cloudbees.io`.
7. Supply the dedicated reviewer account through the portal.
8. Upload the demo video.
9. Run the portal's automated checks.
10. Submit for public review.

Do not perform the final submission without explicit user authorization at
action time.
