# Release checklist

Three separate release artifacts share these skills and one MCP server. Each has
its own review, version record and rollback:

| Artifact | Source in this repo | Where it is submitted |
| --- | --- | --- |
| OpenAI plugin (ChatGPT + Codex) | `packages/openai/` | OpenAI plugin portal, <https://platform.openai.com/plugins> |
| Claude connector | none (the MCP URL only) | Anthropic connector directory |
| Claude Code plugin | `packages/claude/` + `.claude-plugin/marketplace.json` | This repo as a marketplace, then the official Anthropic plugin marketplace |

## 1. Platform prerequisites (outside this repo)

Do not submit until every item is true in **production**; verify on Preview first.

- [ ] `https://mcp-api.convai.com/mcp` is public over trusted TLS and returns `401` with
      `WWW-Authenticate: Bearer ... resource_metadata="https://mcp-api.convai.com/.well-known/oauth-protected-resource"`.
- [ ] `/.well-known/oauth-protected-resource` lists `resource`, `authorization_servers: ["https://login.convai.com"]`
      and `scopes_supported` **without** `knowledge-bank:write` (reserved until upload/delete tools ship).
- [ ] `https://login.convai.com/.well-known/oauth-authorization-server` returns metadata with
      `authorization_response_iss_parameter_supported: true`.
- [ ] Production `OAUTH_CLIENTS` registers:
      `claude` (`https://claude.ai/api/mcp/auth_callback`, `https://claude.com/api/mcp/auth_callback`),
      `claude-code` (`http://localhost:8080/callback`, matches `packages/claude/.mcp.json`),
      `chatgpt` (`https://chatgpt.com/connector_platform_oauth_redirect`),
      `codex` (`http://127.0.0.1:1456/callback`). Re-check against the exact redirect URI the
      OpenAI portal shows before submitting.
- [ ] Production `OAUTH_ALLOWED_RESOURCES=https://mcp-api.convai.com/mcp`; Character API
      `CONVAI_PAT_AUDIENCE` includes that resource.
- [ ] Cloud Armor on the production Auth backend allows `POST /auth/oauth/authorize/decision`,
      `POST /auth/oauth/token` and `DELETE /auth/personal-access-tokens/*` for `login.convai.com`.
- [ ] Knowledge bank owner accepts OAuth tokens for `list_knowledge_documents`. If not, remove
      `knowledge-association` and `knowledge-bank:read` from this release.
- [ ] OpenAI requirements on the MCP server: per-tool `securitySchemes` (`oauth2` + scopes),
      `_meta["mcp/www_authenticate"]` on auth errors, and the domain verification token served at
      `https://mcp-api.convai.com/.well-known/openai-apps-challenge`.
- [ ] Every tool has `title`, `readOnlyHint`, `destructiveHint`, `openWorldHint` (already true in the catalog).
- [ ] Review account: a Convai account with at least two characters and one knowledge document,
      no MFA, reachable without VPN. Store its credentials in the team password manager, never here.
- [ ] Public pages exist: product page, <https://convai.com/privacy-policy>, <https://convai.com/tos>,
      support (`support@convai.com`) with the [support runbook](support-runbook.md) content.

## 2. Build and verify the packages

```bash
python3 scripts/build.py                     # copy shared/skills into both packages
python3 scripts/validate.py --catalog ../convai-api-mcp/src/convai_api_mcp/data/operation-catalog.v1.json
claude plugin validate packages/claude --strict
claude plugin validate .
```

Test against Preview before production exists:

```bash
python3 scripts/build.py --mcp-url https://mcp-api-preview.convai.com/mcp --out dist/preview
claude --plugin-dir dist/preview/claude      # then /mcp -> convai -> Authenticate
```

Record for every release (in `CHANGELOG.md`): plugin version, git SHA, MCP image digest,
operation catalog version, Auth release, client versions tested, results of each review case in
`shared/review-cases.json`.

## 3. OpenAI (ChatGPT and Codex) - one submission

1. Add brand assets to `packages/openai/assets/` (logo, composer icon, 2-3 screenshots) and
   reference them in `plugin.json` under `extensions.com.openai.interface`
   (`logo`, `composerIcon`, `screenshots`, `brandColor`). Confirm `category` in the portal.
2. `python3 scripts/build.py --zip` produces `dist/convai-character-authoring-openai-<version>.zip`.
3. Portal -> **Create plugin** -> **With MCP**, using the verified Convai business identity.
   - **Info**: copy name, short and long description from `packages/openai/plugin.json`; website,
     support, privacy and terms URLs.
   - **MCP**: server URL `https://mcp-api.convai.com/mcp`; authentication OAuth, client ID
     `chatgpt`; copy the portal's redirect URI into production `OAUTH_CLIENTS` if it differs.
     Scan tools and review names, descriptions, annotations and security schemes.
   - **Skills**: upload the zip (or the `skills/` folder from it).
   - **Prompts**: `starterPrompts` from `shared/review-cases.json`.
   - **Testing**: the 5 positive and 3 negative cases from `shared/review-cases.json` plus the
     review account.
   - **Global**: choose availability; **Submit** with release notes from `CHANGELOG.md`.
4. After approval: publish to a limited audience, install from a clean ChatGPT account and a
   clean Codex install (`codex` -> Plugins), complete OAuth and run the review cases, then widen.

## 4. Claude connector (claude.ai, Desktop, mobile)

1. In a test Claude account: **Settings -> Connectors -> Add custom connector**, URL
   `https://mcp-api.convai.com/mcp`, Advanced settings -> OAuth Client ID `claude`. Run the
   review cases, disconnect and reconnect, and check a Team/Enterprise owner can enable it.
2. Submit the remote server through Anthropic's connector directory form (see the
   [custom connector guide](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
   and [directory policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy)).
   Provide: server URL, OAuth client ID `claude`, at least three use cases (use the positive
   review cases), review account, privacy policy, support contact and proof Convai owns
   `convai.com`.

## 5. Claude Code plugin

1. Tag the release: bump the version in all three manifests (validation fails otherwise),
   update `CHANGELOG.md`, merge, then `git tag v<version> && git push --tags`. CI attaches zips.
2. Install from the public Convai marketplace in a fresh environment:
   ```text
   /plugin marketplace add Conv-AI/ConvAI-Agent-Plugin
   /plugin install convai-character-authoring@convai
   /mcp            # convai -> Authenticate, finish Convai sign-in and consent
   ```
   Check skill discovery, a read and a write review case, `/plugin update`, and uninstall.
3. Submit `Conv-AI/ConvAI-Agent-Plugin` (plugin path `packages/claude`, pinned tag) to the
   official Anthropic plugin marketplace through the current submission form. Keep the Convai
   marketplace as the fallback until the official listing and upgrades are proven.

## Rollback

- Claude Code: users on the Convai marketplace pin `Conv-AI/ConvAI-Agent-Plugin@v<previous>`;
  re-point the `main` marketplace by reverting the release commit.
- OpenAI / Claude connector: unpublish or revert the listing in the portal; the MCP server and
  Auth changes roll back through their own infrastructure releases.
