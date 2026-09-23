# Support runbook

Public contact: `support@convai.com`. Ask users for the client (ChatGPT, Codex, Claude,
Claude Code) and version, the time of the failure and any request ID in the error.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| "Session expired" on the Convai consent page | Convai sign-in older than an hour | Click **Log in again**; the flow resumes at consent |
| Browser shows "redirect_uri is not registered" | Client redirect not in production `OAUTH_CLIENTS` | Add the exact redirect for that client ID, redeploy Auth |
| 502 page after clicking Allow | Cloud Armor blocking the consent/token request | Check the allow rules in the release checklist |
| Codex / Claude Code "couldn't connect" after consent | Local login listener closed (login timed out) | Start sign-in again and finish consent within 10 minutes |
| Tool error "not authorized" / plan error | Account plan or workspace role does not allow the operation | Explain the plan limit; nothing is wrong with the connection |
| All tools fail with 401 after working | Refresh token revoked or account disabled | Disconnect and reconnect the connector/plugin |

## Reconnect steps

- **Claude**: Settings -> Connectors -> Convai -> Disconnect, then Connect.
- **Claude Code**: `/mcp` -> convai -> Clear authentication -> Authenticate.
- **ChatGPT**: Settings -> Apps -> Convai -> Disconnect, then reconnect.
- **Codex**: `codex mcp logout convai` then `codex mcp login convai` (or reconnect from Plugins).

## Escalation

Auth issues -> Authentication owners (`ConvAI-Authentication`). Tool errors -> MCP owners
(`convai-api-mcp`) with the request ID. Character data issues -> Character API owners.
