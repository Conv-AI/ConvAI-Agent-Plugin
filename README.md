# Convai Character Authoring - agent plugins

Plugin packages that let ChatGPT, Codex, Claude and Claude Code build and manage Convai AI
characters through the Convai MCP server (`https://mcp-api.convai.com/mcp`). Users sign in
with their Convai account (OAuth 2.1 at `https://login.convai.com`); the packages contain no
credentials.

```text
shared/
  skills/                      # source of truth for every platform
    character-inspect/         # read-only lookup and summaries
    character-author/          # create / edit / delete, narrative, functions
    character-version-review/  # diff, release, promote, roll back
    knowledge-association/     # connect existing knowledge documents
  review-cases.json            # starter prompts + 5 positive / 3 negative review cases
packages/
  openai/                      # OpenAI portable plugin (ChatGPT + Codex)
    plugin.json  mcp.json  skills/
  claude/                      # Claude Code plugin
    .claude-plugin/plugin.json  .mcp.json  skills/
.claude-plugin/marketplace.json  # this repo is a Claude Code marketplace
scripts/build.py               # sync skills, --check for drift, --zip
scripts/validate.py            # release checks (versions, prod URL, scopes, secrets, tool names)
```

`packages/*/skills/` are generated: edit `shared/skills/` and run `python3 scripts/build.py`.
CI fails if they drift.

## OpenAI resubmission status (0.1.5)

This candidate updates the skills and listing against the [OpenAI plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). It is not a declaration that the remote service passed policy review. The rejection email did not identify a specific offending behavior. Changes to wording alone cannot resolve a backend policy violation.

The package now instructs the host to preserve safeguards, treat retrieved content as data, limit sensitive-data access and check historical configurations before activation. These instructions are not a server security boundary. This repository contains no MCP server implementation, deployed tool annotations or published privacy-policy source.

Before resubmitting, complete these checks in the MCP service and review portal:

- Enforce the intended safety boundaries on the server, including direct create/update requests, generation, cloning, release, promotion and draft restoration. Verify that model selection and nested configuration objects cannot bypass those boundaries. The is_uncensored label is a reason to investigate behavior, not proof of a policy violation. This package conservatively excludes those entries from authoring and activation.
- Inspect the actual tools/list response. Confirm explicit boolean readOnlyHint, destructiveHint and openWorldHint annotations match each operation. Describe auto-created Experiences, overwrites, publication and outbound network contacts accurately. Each callable operation must be individually exposed; discovery must not become a generic executor for unreviewed tools.
- Check authorization for every character, version, document, function and external-server ID. Verify that tool results redact stored credentials and that external-server testing cannot reach unauthorized destinations. Configuration of a function must remain distinct from executing it.
- Verify the published privacy policy covers character content, knowledge associations, character conversation history, recipients, retention and user controls. Validate scopes and secure sign-in; do not put reviewer credentials in this repository or ZIP.
- Run the five positive and three negative cases in shared/review-cases.json, plus supplementalNegative internally, against isolated fixtures. Record actual results and backend rejection evidence separately; verificationStatus starts as not_run. Passing the package validator does not run these scenarios. Test the supported ChatGPT desktop and mobile flows.
- Provide an accessible walkthrough, working reviewer account, release notes and any requested policy attestations in the submission portal. The build currently packages packages/openai only: shared/review-cases.json is preparation material and is not automatically imported from the ZIP. Enter the cases in the portal's review fields and confirm they were saved.
- Request the specific policy section and observed failure from the review team if the rejection remains unclear. Do not claim the issue is resolved until the corresponding behavior has been verified.

After verification, build with `python3 scripts/build.py --zip` and upload the versioned OpenAI ZIP in dist/. See the [submission guide](https://developers.openai.com/plugins/deploy/submission) for portal steps.

## Install

**Claude Code**

```text
/plugin marketplace add Conv-AI/ConvAI-Agent-Plugin
/plugin install convai-character-authoring@convai
/mcp        # convai -> Authenticate
```

**Claude (web, Desktop)**: Settings -> Connectors -> Convai (after directory listing), or add a
custom connector with URL `https://mcp-api.convai.com/mcp` and OAuth Client ID `claude`.

**ChatGPT and Codex**: install *Convai Character Authoring* from the plugin directory (after
OpenAI approval) and sign in to Convai when prompted.

## Develop

```bash
python3 scripts/build.py && python3 scripts/validate.py
claude plugin validate packages/claude --strict && claude plugin validate .
```
