---
name: onboard-repo-to-unify
description: >
  Onboard a GitHub repository to CloudBees Unify by creating one or more components
  and triggering a security scan. Use when the user says things like "onboard this
  repo to Unify", "add this project to CloudBees Unify", "register this repo in
  Unify", "create a Unify component for this repo", "set up this repo in CloudBees",
  or "connect my repo and run a security scan".
allowed-tools:
  - mcp__unify-mcp-server__*
  - Bash
---

# Onboard Repo to CloudBees Unify

## Prerequisites

Before starting, confirm the user has:
- Admin access to their SCM provider (GitHub, GitLab, Bitbucket, or Gerrit)
- Ability to create API tokens or credentials in that provider

If either is missing, stop and advise them to get the necessary permissions first.

## Workflow

1. **Verify Unify connection** — call `user_whoami`. If it errors, tell the user to
   check `/mcp` and run `/reload-plugins`.

2. **Get org ID** — call `organizations_list_suborganizations`. Auto-select if only
   one exists; otherwise ask the user to pick.

3. **Find SCM endpoint** — call `endpoint_list` (`contributionTypes:
   "cb.platform.endpoint-type"`).
   - If a matching endpoint exists: confirm the name and proceed.
   - If none exist: instruct the user to go to Unify → org Settings → Integrations
     → "Create integration", select their SCM provider, fill in the form, and save.
     Ask them to confirm when done, then retry.

4. **Get repo details** — run `git remote get-url origin` for the URL and
   `git symbolic-ref refs/remotes/origin/HEAD | sed 's|.*/||'` for the default
   branch (fall back to `main`).

5. **Check for existing components** — call `components_list`. If this repo URL is
   already registered, show the existing component and confirm before proceeding.

6. **Create component(s)** — call `components_create` with `name`, `endpoint_id`,
   `organization_id`, `repository_url`, `default_branch`. The component name
   defaults to the last segment of the repo name. Do not offer to create duplicate components for the same repo URL.

   Creating a component automatically triggers a security scan in the background.

7. **Guide the user to view scan results** — after the component is created:
   - Ask them to open the component in Unify and go to the **Runs** tab to monitor
     scan progress.
   - Once the scan completes, direct them to the **Security Center** tab to view
     results.

8. **Summarize and suggest next steps** — confirm what was created (name, repo URL,
   branch, org), then offer:
   - Triage and remediate vulnerabilities found in the scan
   - Create additional components for other repositories
   - Set up CI/CD workflows (Unify native, GitHub Actions, CloudBees CI, Jenkins)
   - Explore Feature Management for controlled rollouts
