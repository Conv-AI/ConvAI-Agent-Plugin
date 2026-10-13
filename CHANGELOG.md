# Changelog

## 0.1.5

- Add general-audience authoring, safeguard preservation, untrusted-content handling and data-minimization instructions to the shared skills.
- Apply safety checks to cloning and version activation, and explain downstream effects of function and external-server associations.
- Make automatic asset/Experience creation opt-in in the authoring workflow and make release promotion explicit.
- Clarify listing scope, add safety-focused review cases and preserve additional regression scenarios. Cases are unexecuted until tested against a review account.
- Document backend and submission verification still needed. Skill changes do not implement server-side policy enforcement or guarantee approval.

## 0.1.4

- Skill descriptions and prose no longer say "MCP" or "model" ("external tool servers", "response settings"); tool names are unchanged.

## 0.1.3

- OpenAI subtitle is "Build Convai game characters" ("AI characters" read as a reference to another AI platform); dropped the `conversational-ai` keyword.

## 0.1.2

- OpenAI listing text no longer names models or agents: new About text, plain description, and skill descriptions say "response settings" instead of "model".

## 0.1.1

OpenAI review fixes.

- OpenAI listing category is now Developer Tools; the About text leads with the plugin's purpose and states its limits.
- `character-author` no longer mentions `test_function`; production MCP does not expose function execution.

## 0.1.0

First submission candidate.

- Skills: `character-inspect`, `character-author`, `character-version-review`, `knowledge-association`.
- MCP: `https://mcp-api.convai.com/mcp` (OAuth 2.1 via `https://login.convai.com`).
- Scopes requested: `character:read`, `character:write`, `backstory:generate`, `chat-history:read`, `knowledge-bank:read`, `knowledge-bank:write` (conditional on character writes that touch knowledge associations).
- Record at release: MCP image digest, catalog version, Auth release, client versions tested.
