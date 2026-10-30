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
  review-cases.json            # starter prompts and synthetic verification scenarios
packages/
  openai/                      # OpenAI portable plugin (ChatGPT + Codex)
    plugin.json  mcp.json  skills/
  claude/                      # Claude Code plugin
    .claude-plugin/plugin.json  .mcp.json  skills/
  grok-bot/                    # Grok Bot plugin (Cursor plugin format)
    .cursor-plugin/plugin.json  mcp.json  assets/  skills/  LICENSE (Apache-2.0)
.claude-plugin/marketplace.json  # this repo is a Claude Code marketplace
.cursor-plugin/marketplace.json  # and a Cursor / Grok Bot marketplace (packages/grok-bot)
scripts/build.py               # sync skills, --check for drift, --zip
scripts/validate.py            # release checks (versions, prod URL, scopes, secrets, tool names)
```

`packages/*/skills/` are generated: edit `shared/skills/` and run `python3 scripts/build.py`.
CI fails if they drift.

## Install

### ChatGPT and Codex

Install **Convai Agent Authoring** from your application's plugin directory and sign
in with your Convai account when prompted. Review the requested permissions before
approving access. You do not need an API key, the Convai CLI, or a local MCP server.

The published OpenAI package is **0.2.9**, with package ID
`convai-character-authoring`. The **0.3.0** rename to `convai-agent-authoring` in
this repository does not establish that the renamed package is published.

For a first read, ask: "List my Convai agents." Choose an agent from the returned
list and ask for its saved configuration. Specify the intended Workspace when
applicable. Installing the plugin does not grant additional Workspace, role, or
plan permissions.

### Claude Code

```text
/plugin marketplace add Conv-AI/ConvAI-Agent-Plugin
/plugin install convai-agent-authoring@convai   # renamed from convai-character-authoring in 0.3.0
/mcp        # convai -> Authenticate
```

### Claude web and Desktop

Use Settings -> Connectors -> Convai when available in your directory, or add a
custom connector with URL `https://mcp-api.convai.com/mcp` and OAuth Client ID `claude`.

## Capabilities and limits

The plugin supports authorized agent inspection, character authoring, narrative
editing, version review and release, existing knowledge-document associations,
and requested conversation-history reads. Confirm changes before writing.

It does not upload knowledge documents, execute function code, or start live
voice conversations. Hosted OAuth cannot discover the knowledge library; connect
an existing document only when its authorized ID is known. Use the connected
tools' schemas and advertised Workspace support rather than assuming every
operation is available.

## Privacy and support

Review Convai's [Privacy Policy](https://convai.com/privacy-policy) and
[Terms of Service](https://convai.com/tos) before connecting your account.
Use the [Convai Developer Forum](https://forum.convai.com) for support.

## Develop

```bash
python3 scripts/build.py && python3 scripts/validate.py
python3 -m unittest discover -s tests
claude plugin validate packages/claude --strict && claude plugin validate .
```

Build local archives with `python3 scripts/build.py --zip`. Building an archive
does not publish a directory listing or change a hosted MCP deployment.
See [CHANGELOG.md](CHANGELOG.md) for package changes. Release coordination and
non-production verification are maintained separately from these public instructions.
