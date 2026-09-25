# Submission answers

Copy-paste text for the OpenAI plugin portal and the Claude directory portals.
Keep it in sync with `packages/openai/plugin.json` and `shared/review-cases.json`.
Credentials never go in this repo: keep the review account in the team password
manager and paste it into the portals directly.

## Shared listing

| Field | Value |
| --- | --- |
| Name | Convai Character Authoring |
| Tagline (Claude, max 55) | Build and manage Convai AI characters |
| Short description (OpenAI) | Build and manage Convai AI characters. |
| Developer / company | Convai (Convai Technologies Inc.) |
| Website | https://convai.com |
| Documentation | https://github.com/Conv-AI/ConvAI-Agent-Plugin#readme |
| Privacy policy | https://convai.com/privacy-policy |
| Terms | https://convai.com/tos |
| Support | support@convai.com |
| Logo / icon | `packages/openai/assets/logo.png` (512x512), `composer-icon.png` (128x128) |
| Brand color | `#29B355` |
| Suggested categories | Developer tools, Productivity (OpenAI: confirm against the portal list) |
| MCP server | `https://mcp-api.convai.com/mcp` (streamable HTTP, universal URL) |
| Authorization server | `https://login.convai.com` |

### Description (Claude max 2,000 characters; also OpenAI long description)

Convai Character Authoring connects your AI assistant to your Convai account so you can
build and manage conversational AI characters for games, virtual worlds and interactive
experiences without leaving the chat.

Sign in with your Convai account to:
- List and inspect your characters: backstory, model, voice, language, narrative design,
  functions, connected MCP servers and knowledge documents.
- Create characters from a name and backstory, or generate a backstory and starter
  conversation to get going.
- Edit character settings and narrative design (sections, triggers and decisions).
- Review changes: diff the draft against released versions, release a new version,
  promote or roll back versions, or discard draft edits.
- Connect or disconnect existing knowledge bank documents.

Every change is shown and confirmed before it is written to your account, and destructive
actions such as deleting a character need an explicit confirmation. Access follows your
Convai plan and workspace role. You can revoke access at any time by disconnecting the app.

## Claude connector portal

- **Connection:** Universal URL `https://mcp-api.convai.com/mcp`, streamable HTTP.
- **Use cases:**
  1. Inspect and summarize existing Convai characters (read).
  2. Create a new character and refine its backstory, voice and model (write).
  3. Review a character's draft changes and release or roll back a version (read + write).
  4. Link existing knowledge bank documents to a character (write).
- **What users need:** a Convai account (https://convai.com). Knowledge bank features follow
  the account's plan.
- **Reads or writes:** both.
- **Authentication:** OAuth. Without CIMD deployed: Anthropic-held credentials, client ID
  `claude`, public client with PKCE S256, redirect `https://claude.ai/api/mcp/auth_callback`
  (confirm with mcp-review@anthropic.com first; email below). With CIMD deployed: CIMD.
- **Data handling:** first-party API (Convai owns the MCP server and the APIs behind it); no
  personal health data; no sponsored content.
- **Test & launch:** provide the review account and these steps:
  1. In Claude, add the Convai connector and click Connect.
  2. Sign in at login.convai.com with the review account and click Allow on the consent page.
  3. Try: "List my Convai characters", "Create a Convai character named Captain Mira ...",
     "What changed in Review Guide's draft?", "Which knowledge documents does Review Guide use?".
  Confirm you ran every tool yourself as a custom connector (client ID `claude` under
  Advanced settings).

### Email to mcp-review@anthropic.com (before the portal submission)

> Subject: Convai connector - OAuth client for directory submission
>
> We're submitting Convai Character Authoring (MCP server `https://mcp-api.convai.com/mcp`,
> authorization server `https://login.convai.com`). We'd like to use Anthropic-held
> credentials with `client_id=claude`, a public client (no secret) using PKCE S256 and
> redirect `https://claude.ai/api/mcp/auth_callback`. Our token endpoint accepts `client_id`
> in the form body (`token_endpoint_auth_method: none`). Can you use a public client, or do
> you require a client secret, and which token endpoint auth method do you use?

## Claude plugin directory

- Repository: `https://github.com/Conv-AI/ConvAI-Agent-Plugin` (must be public), plugin path
  `packages/claude`, tag `v<version>`.
- The plugin uses the pre-registered `claude-code` OAuth client on callback port 8080.

## OpenAI portal (ChatGPT + Codex)

- **MCP:** server URL above; OAuth with predefined client ID `chatgpt`; check the portal's
  redirect URI equals `https://chatgpt.com/connector_platform_oauth_redirect`.
- **Domain verification:** serve the portal's token at
  `https://mcp-api.convai.com/.well-known/openai-apps-challenge` before verifying.
- **Skills:** upload `dist/convai-character-authoring-openai-<version>.zip`
  (`python3 scripts/build.py --zip`).
- **Prompts:** `starterPrompts` in `shared/review-cases.json`.
- **Testing:** the 5 positive and 3 negative cases in `shared/review-cases.json`, plus the
  review account (no MFA, at least two characters incl. "Review Guide", one knowledge
  document).
- **Release notes:** the current version's section of `CHANGELOG.md`.
