---
name: onboard-repo-to-unify
description: >
  Onboard a GitHub repository to CloudBees Unify by creating one or more components
  and pointing to where security scan results appear. Use when the user says things like "onboard this
  repo to Unify", "add this project to CloudBees Unify", "register this repo in
  Unify", "create a Unify component for this repo", "set up this repo in CloudBees",
  or "connect my repo and run a security scan".
allowed-tools:
  - mcp__unify-mcp-server__*
  - mcp__plugin_cloudbees-unify_unify-mcp-server__*
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

2. **Get org ID** — ask which organization or sub-organization the component belongs
   in, suggesting `selected_organization` from `user_whoami`. Resolve the name with
   `organizations_list` and `name` (a plain, case-insensitive fragment; no wildcards):
   - One match: use its `id`.
   - Several matches: list each `displayName`, `domainName`, and `id`, and ask the
     user which one to use.
   - No match: a name search doesn't return sub-organizations. Call
     `organizations_list` with `nested: true` and no `name`, and look for the name in
     `childOrganizations` at every depth. If it's still not found, say so and ask the
     user for the org ID. Don't guess.

   Note the top-level organization the selected org sits under (itself, if it has no
   parent); step 5 needs it.

3. **Find SCM endpoint** — call `endpoint_list` with `resourceId` set to the org ID,
   `contributionTypes: "cb.platform.endpoint-type"`, and `parents: true` (a
   sub-organization usually inherits its parent's integrations). Follow `nextCursor`
   until it's absent. This type also returns non-SCM integrations such as container
   registries, Jira, and CloudBees CI; keep only endpoints whose `contributionId` names
   the repo's SCM provider (for example `cb.github.github-app-endpoint-type`).
   - If a matching endpoint exists: confirm the name and proceed.
   - If none exist: instruct the user to go to Unify → org Settings → Integrations
     → "Create integration", select their SCM provider, fill in the form, and save.
     Ask them to confirm when done, then retry.

4. **Get repo details** — run `git remote get-url origin` for the URL and
   `git symbolic-ref refs/remotes/origin/HEAD | sed 's|.*/||'` for the default
   branch (fall back to `main`).

5. **Check for existing components** — call `services_list` with `organizationId` and
   `typeFilter: COMPONENT_FILTER`, and compare each `repositoryUrl` to the repo URL
   (ignore a trailing `.git`; treat `git@host:owner/repo` and `https://host/owner/repo`
   as the same). Use the top-level org ID: its results include sub-organization
   components. If this repo URL is already registered, show the existing component and
   confirm before proceeding.

6. **Create component(s)** — call `services_add` with `organizationId` (the org
   selected in step 2, not the top-level one from step 5), `name`,
   `serviceType: "COMPONENT"`, `endpointId`, `repositoryUrl` (the HTTPS clone URL),
   and `defaultBranch`. The component name defaults to the last segment of the repo
   name. Do not offer to create duplicate components for the same repo URL; if the
   user mentions several services in one repo, explain that one repo URL backs one
   component and ask how they want to proceed. Show the values and wait for the
   user's OK before calling `services_add`.

7. **Point the user to scan results** — creating a component doesn't confirm that a
   security scan started, finished, or passed, so don't claim any of that. Ask them to
   open the component in Unify and check the **Runs** tab for scan activity and the
   **Security Center** tab for findings.

8. **Summarize and suggest next steps** — confirm what was created (name, repo URL,
   branch, org), then offer:
   - Triage and remediate vulnerabilities once they appear in Security Center
   - Create additional components for other repositories
   - Set up CI/CD workflows (Unify native, GitHub Actions, CloudBees CI, Jenkins)
   - Explore Feature Management for controlled rollouts
