# Convai Agent Authoring - agent plugins

Plugin packages that let ChatGPT, Codex, Claude and Claude Code build and manage Convai
agents through the Convai MCP server (`https://mcp-api.convai.com/mcp`). Users sign in
with their Convai account (OAuth 2.1 at `https://login.convai.com`); the packages contain no
credentials.

```text
shared/
  skills/                      # source of truth for every platform
    agent-inspect/             # read-only lookup and summaries
    agent-author/              # create / edit / delete, narrative, functions
    agent-version-review/      # diff, release, promote, roll back
    agent-knowledge/           # connect existing knowledge documents
  review-cases.json            # starter prompts + the 5 positive / 3 negative cases submitted to OpenAI
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

## OpenAI listing status (0.2.9)

0.2.9 was approved and published in the ChatGPT plugin directory on 2026-10-27. Earlier submissions (0.1.x and early 0.2.x) were rejected without a specific reason; see CHANGELOG.md for what changed. Lessons that apply to other directories:

- The review scans the live `tools/list` of `https://mcp-api.convai.com/mcp`, not only this package. Every tool the reviewer sees must work for the reviewer's account and sign-in method, and tool descriptions, the listing and the skills must not mention tools the server does not register. The hosted server therefore hides API-key-only tools from OAuth callers and does not expose function execution or external tool-server management.
- The portal identifies ChatGPT to the authorization server with an OAuth client ID metadata document URL; the authorization server must recognize that client and its exact redirect URI before Connect works.
- The reviewer account must already hold every plan entitlement the test cases need; the review cannot include a purchase.
- Listing text says "agents", not "AI characters". Explain in the submission context that Convai is the product brand, how to sign in (email and password on the Convai sign-in page, then Approve), and what the plugin deliberately does not do. Never put reviewer credentials in this repository.

After a change, build with `python3 scripts/build.py --zip` and upload the versioned OpenAI ZIP in dist/ as an update to the existing plugin. See the [submission guide](https://developers.openai.com/plugins/deploy/submission) for portal steps.

## Install

**Claude Code**

```text
/plugin marketplace add Conv-AI/ConvAI-Agent-Plugin
/plugin install convai-character-authoring@convai   # plugin ID is unchanged
/mcp        # convai -> Authenticate
```

**Claude (web, Desktop)**: Settings -> Connectors -> Convai (after directory listing), or add a
custom connector with URL `https://mcp-api.convai.com/mcp` and OAuth Client ID `claude`.

**ChatGPT and Codex**: install *Convai Agent Authoring* from the plugin directory and sign in to Convai when prompted.

## Develop

```bash
python3 scripts/build.py && python3 scripts/validate.py
claude plugin validate packages/claude --strict && claude plugin validate .
```
