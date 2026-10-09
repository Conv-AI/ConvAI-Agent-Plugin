---
name: character-inspect
description: Look up the user's Convai characters and explain how one is configured - backstory, voice, language, response settings, narrative, functions, connected external tools and knowledge documents. Use when the user asks to list, find, show, summarize or audit a Convai character without changing it.
---

# Inspect a Convai character

Read-only. Never call a create, update, delete, release or attach tool from this skill.

## Workflow

1. **Find the character.** If the user gave a character ID, call `get_character` directly. Otherwise call `list_characters` and match by name. If several characters share the name, show the candidates (name, ID, last updated) and ask which one.
2. **Read the configuration** with `get_character`. Report only what the user asked about; for a general summary cover name, backstory (condensed), response settings, voice, language, and whether it has narrative design, functions or knowledge documents.
3. **Drill down only when asked:**
   - Narrative: `list_narrative_sections`, `get_narrative_section`, `list_narrative_triggers`.
   - Functions: `list_functions` (with the character ID for attachment status), `get_function`.
   - External tool servers: `list_character_mcp_servers`, `list_external_mcp_servers`.
   - Knowledge: `list_knowledge_documents`.
   - Versions: `list_character_versions` (use the `character-version-review` skill for comparisons).
   - Option catalogs: `list_supported_models`, `list_voices`, `list_languages`.
4. **Chat history is sensitive.** Call `list_chat_history`, `get_chat_history` or `get_chat_interaction` only when the user explicitly asks about conversations. Summarize; do not paste full transcripts unless asked, and never request third-party tool results unless the user needs them.

## Output

- Lead with the answer, then the supporting fields.
- Always include the character ID so follow-up edits target the right character.
- If a tool returns an authorization or plan error, say what is not available and suggest checking the Convai plan or workspace role; do not retry with different identifiers.
