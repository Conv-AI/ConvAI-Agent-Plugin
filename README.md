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

- Server side, not package side, decided the outcome. The portal scans the live `tools/list` from `https://mcp-api.convai.com/mcp`, so every tool it sees must work for the reviewer account and match what the listing and skills say.
  - Tools the reviewer's OAuth token cannot use are hidden from bearer callers (`list_knowledge_documents` is API-key only; convai-api-mcp PR 33).
  - External MCP server tools are disabled on the hosted server (`CONVAI_MCP_EXTERNAL_MCP_TOOLS_ENABLED=false`, PR 37) because no plan grants `MCP_TOOLS_API`; tool descriptions must not name unregistered tools (PR 38).
  - Function execution (`test_function`) stays disabled.
- OAuth: the portal sends the CIMD client ID `https://chatgpt.com/oauth/client.json`, which OpenAI currently serves as 404. Convai Authentication carries a static `OAUTH_CLIENTS` entry for it with redirect `https://chatgpt.com/connector_platform_oauth_redirect` (gcp-app-infra-iac PR 9853).
- The reviewer account (Scale plan) owns the Workspace and agent used by the test cases. Chat history needs Scale or higher; core authoring needs Professional or higher.
- Listing text says "agents", not "AI characters"; "Convai" is the brand, not another AI assistant. Put the account, sign-in steps (email and password on the Convai sign-in page, then Approve) and scope notes in the portal's submission context, never in this repository.

Follow-ups are tracked under Jira epic CORE-2009.

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
