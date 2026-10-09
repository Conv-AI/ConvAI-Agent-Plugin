---
name: character-author
description: Create or edit a Convai character - write or generate a backstory, pick voice, language and response settings, and design narrative sections, triggers and decisions. Use when the user asks to create, build, clone, update, rename, redesign or delete a Convai character or its narrative.
---

# Author a Convai character

Every change here is written to the user's Convai account. Confirm before writing; never retry a failed write automatically.

## Before any write

1. **Identify the target.** For edits, resolve the character with `list_characters` / `get_character` and state its name and ID.
2. **Read current state first** with `get_character` (and the relevant `get_narrative_*` / `get_function` tool) so the change is computed against what is saved now.
3. **Show the material change** - the fields that will change, old versus new - and get the user's go-ahead. The host's tool-approval prompt is the final confirmation; do not bypass it.

## Create

1. Gather a name and a backstory. If the user wants help writing one, call `generate_character_backstory` (it does not modify anything) and let the user edit the result.
2. Call `create_character` with the name and backstory. Leave model, voice, visibility and assets unset unless the user chose them; choose from `list_supported_models`, `list_voices` and `list_languages`, never invent values.
3. Offer `generate_starter_conversation` for sample opening messages.
4. `clone_character` copies an existing visible character - use it when the user asks to start from one.

## Edit

- `update_character` changes only the fields you send; omitted fields keep their saved value. Send only what the user asked to change.
- Edits land on the editable **draft**. Tell the user the live version is unchanged until they release it (see `character-version-review`).
- Narrative design: `create_narrative_section`, `update_narrative_section`, `create_narrative_trigger`, `update_narrative_trigger`, `add_narrative_decision`, `edit_narrative_decision`, `set_narrative_start_section`. Explain the resulting flow (start section, choices, triggers) after changes.
- Functions and external MCP servers: `create_function`, `update_function`, `attach_function`, `detach_function`, `attach_external_mcp_server`, `detach_external_mcp_server`. `test_external_mcp_server` contacts an external system - say which server it will call before calling it.

## Destructive operations

`delete_character`, `delete_function`, `delete_narrative_section`, `delete_narrative_trigger` and `delete_narrative_decision` are permanent. Name exactly what will be deleted, ask for explicit confirmation in the conversation, and only then call the tool. Never delete as a side effect of another request.

## After writing

Report what changed with the character ID. If a write fails, show the error, state that nothing further was attempted, and let the user decide the next step.
