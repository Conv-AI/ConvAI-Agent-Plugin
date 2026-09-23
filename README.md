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
scripts/build.py               # sync skills, --check for drift, --zip, --mcp-url test builds
scripts/validate.py            # release checks (versions, prod URL, scopes, secrets, tool names)
docs/                          # release checklist, privacy data map, support runbook
```

`packages/*/skills/` are generated: edit `shared/skills/` and run `python3 scripts/build.py`.
CI fails if they drift.

## Install

**Claude Code**

```text
/plugin marketplace add Conv-AI/convai-agent-plugins
/plugin install convai-character-authoring@convai
/mcp        # convai -> Authenticate
```

**Claude (web, Desktop)**: Settings -> Connectors -> Convai (after directory listing), or add a
custom connector with URL `https://mcp-api.convai.com/mcp` and OAuth Client ID `claude`.

**ChatGPT and Codex**: install *Convai Character Authoring* from the plugin directory (after
OpenAI approval) and sign in to Convai when prompted.

## Develop

```bash
python3 scripts/build.py && python3 scripts/validate.py \
  --catalog ../convai-api-mcp/src/convai_api_mcp/data/operation-catalog.v1.json
claude plugin validate packages/claude --strict && claude plugin validate .

# Try it against Preview
python3 scripts/build.py --mcp-url https://mcp-api-preview.convai.com/mcp --out dist/preview
claude --plugin-dir dist/preview/claude
```

Releasing and submitting: [docs/release-checklist.md](docs/release-checklist.md).
