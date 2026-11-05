# Convai Agent Authoring

Create, edit, review and release [Convai](https://convai.com) conversational agents from Claude Code. Ask Claude to list your agents, write or generate a backstory, pick a voice and language, design narrative sections and triggers, connect existing knowledge documents, and compare or release agent versions.

## Install

```text
/plugin marketplace add Conv-AI/ConvAI-Agent-Plugin
/plugin install convai-agent-authoring@convai
/mcp        # convai -> Authenticate
```

Sign in with your Convai account when the browser opens, then approve access. You need a Convai account; create one at https://convai.com.

## Skills

- **agent-inspect**: read-only lookup and summaries of your agents.
- **agent-author**: create, edit, clone or delete agents and their narrative. Asks before every write.
- **agent-version-review**: diff versions, release, promote, roll back or discard draft changes.
- **agent-knowledge**: connect or disconnect existing knowledge bank documents. The hosted connection cannot browse or search your knowledge library, so give the document ID (or pick the document in the [Convai dashboard](https://convai.com/dashboard)); Claude cannot find a document by name alone.

## What the plugin connects to and sends

The plugin contains only skills (Markdown instructions) and one remote MCP server. It runs no local code, hooks or scripts.

- **MCP server**: `https://mcp-api.convai.com/mcp`, operated by Convai. Claude sends tool requests there, including the agent details you ask it to create or change (names, backstories, voice and narrative settings) and identifiers of agents, versions and knowledge documents.
- **Sign-in**: OAuth 2.1 with PKCE through `https://login.convai.com`, using the public client `claude-code` and a local callback on port 8080. The plugin holds no credentials; Claude Code stores the issued token.
- **Scopes requested**: `character:read`, `character:write`, `backstory:generate`, `chat-history:read`, `knowledge-bank:read`, `knowledge-bank:write`.
- Changes are written to your Convai account. The plugin cannot upload or delete knowledge documents, run custom functions, or make purchases.

## Support

support@convai.com · https://convai.com

## License

Proprietary (`LicenseRef-Convai-Proprietary`), Copyright Convai.
