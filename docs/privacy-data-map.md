# Privacy data map

Source for the privacy answers in the OpenAI and Anthropic submission forms. Keep it in
sync with <https://convai.com/privacy-policy>; the policy is authoritative.

## What the plugins contain

The packages hold instructions (skills) and the MCP server URL only. They contain no
credentials and run no code on the user's machine. The client (Claude Code, Codex,
ChatGPT, Claude) keeps the OAuth tokens it receives in its own credential store.

## Data flow

```text
Claude / ChatGPT / Codex
  -> https://mcp-api.convai.com/mcp   (OAuth access token, tool arguments)
  -> Convai Character API / Knowledge API (same user identity)
```

| Data | Direction | Purpose | Stored by Convai |
| --- | --- | --- | --- |
| Convai email and account ID | Sign-in at login.convai.com | Identify the user, issue tokens | Yes, existing account data |
| OAuth tokens | Client <-> Convai | Authorize tool calls | Hashes only; access 1 h, refresh 30 d, revocable |
| Character settings (name, backstory, model, voice, narrative, functions) | Both | Read and edit the user's characters | Yes, as the user's content |
| Knowledge document names and status | Convai -> client | Show and link existing documents | Yes, existing content |
| Chat history (only when the user asks) | Convai -> client | Review conversations with their characters | Yes, existing content |
| Request logs (request ID, tool name, status, latency) | MCP server | Operations and abuse prevention | Yes; confirm retention and that tokens/arguments are not logged before submitting |

Data returned by tools is processed by the client platform (OpenAI or Anthropic) under its own
terms. Users revoke access by disconnecting the connector/plugin; disabling a Convai account
invalidates all of its tokens immediately.
