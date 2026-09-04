---
id: create-feature-flag
title: Implement CloudBees Unify feature flags (ROX SDK)
description: Guidance for writing code that defines and evaluates CloudBees Unify feature flags using the CloudBees Feature Management (ROX) SDK, in whatever language the project uses.
---

# CloudBees Unify Feature Flags — implementation guidance

You are implementing **CloudBees Unify feature flags**. CloudBees Unify Feature
Management is powered by the **CloudBees Feature Management SDK (the "ROX" SDK)**,
which ships for many languages. Use this SDK — **do not** use a generic or
other-vendor feature-flag library.

## Step 1 - Create the flag in Unify
Create the flag using the Unify MCP Server, flags_add tool. Use the name provided by the user.
If flags_add fails, report the exact failure reason. If the flag already exists, continue by reusing the existing flag name. If permissions/tool access fail, stop and ask the user to resolve access before code changes.

## Step 2 — Detect the project's language; do NOT assume one

Decide the language/ecosystem from the repository itself, and use the CloudBees
ROX SDK **for that language**. **Do not default to any particular language** (in
particular, do not assume Node/JavaScript). Detect from repo signals, prioritizing authoritative language type signals such as:

- `package.json` → Node / JavaScript / TypeScript
- `*.ts, tsconfig.json` → Node / TypeScript
- `pom.xml`, `build.gradle` → Java/JVM
- `*.csproj`, `*.sln`, `*.cs`, `nuget.config`, `*.slnx`,  → .NET / C#
- `go.mod` → Go
- `requirements.txt`, `pyproject.toml`, `Pipfile` → Python
- `Gemfile` → Ruby
- `composer.json` → PHP
- For stacks not listed, map to a concrete programming language first (e.g., Swift, Kotlin, C++, React Native), then use that language's exact CloudBees SDK package name and documentation path. If no exact language match is found, ask the user before proceeding.

If repository evidence is insufficient to determine a language with high confidence, stop and ask the user to specify the target language/service. Do not generate implementation code until clarified.
If multiple stacks are present, first identify the specific service/module named in the user request. If no service/module is explicitly named, ask the user to choose the target service before writing code. Do not guess.

## Step 3 — Get the exact SDK + setup for THAT language from the docs

CloudBees ROX SDKs share a family name (`rox-*`) but each language has its own
package and init details — look them up for the **detected** language rather than
guessing:

- Install: `https://docs.cloudbees.com/docs/cloudbees-unify/latest/install-sdk/<language>-sdk`
- Reference: `https://docs.cloudbees.com/docs/cloudbees-unify/latest/sdk-reference/<language>`
- Overview: `https://docs.cloudbees.com/docs/cloudbees-unify/latest/feature-management/get-started-with-feature-flags`

## Step 4 — Follow the universal pattern (same shape in every language)

1. **Declare flags as a container/group** using the SDK's flag types (boolean
   flag, plus string/number variants where available). Prefer these typed
   declarations over ad-hoc booleans.
2. **Register** the flag container with the SDK.
3. **Set up** the SDK with an **SDK key**, and **await** setup once at startup,
   before evaluating flags. The SDK key is generated when a Unify **environment**
   (Development/QA/Staging/Production) is **linked to the application**. Read it
   from configuration/secret/environment variable — **never hardcode it**. If the
   user hasn't provided a key, leave a clearly-marked placeholder and tell them
   where to get it (Unify → the application's environment → SDK key).
4. **Evaluate** flags via the SDK's accessor (e.g. `isEnabled()` / language
   equivalent) at the gate point — not by reading config directly.

## Illustrative example (Node.js) — adapt to the detected language

> This is **one** example of the pattern, not a default. If the project isn't
> Node/JavaScript, use the matching language's `rox-*` package and idioms from the
> docs above — do not copy this verbatim into a non-Node project.

```js
import Rox from 'rox-node';

const flags = {
  enableCheckout: new Rox.Flag(),
  // string/number variants also exist, e.g. new Rox.RoxString('White', ['White','Blue'])
};

async function initFeatureFlags() {
  Rox.register('', flags);                              // namespace ('' = default)
  await Rox.setup(process.env.CLOUDBEES_ROX_SDK_KEY);   // env-linked SDK key
}

if (flags.enableCheckout.isEnabled()) {
  // new behavior
} else {
  // existing behavior
}
```

The same shape applies in every supported language: **declare → register → set up
with the env-linked SDK key → evaluate**, using that language's ROX SDK.
