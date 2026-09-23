---
name: character-version-review
description: Review, compare, release, promote, roll back or discard versions of a Convai character. Use when the user asks what changed in a character, wants to diff versions or the draft, publish or release draft changes, make a version live, revert a change, or throw away draft edits.
---

# Review and release Convai character versions

A character has one editable **draft** and immutable **versions**; one version is **latest** (live).

## Review (read-only)

1. Resolve the character, then call `list_character_versions` to show versions, which is latest, and whether the draft has unreleased changes.
2. Compare with `diff_character_versions` (versions, latest or draft). Prefer the semantic view for people; use raw only when asked. Summarize changes by area: identity/backstory, model/voice/language, narrative, functions, knowledge, MCP servers.

## Change version state (writes - confirm first)

Show the diff that motivates the action and confirm before each call:

- **Release** the draft as a new version: `release_character_version`. Suggest a short release note from the diff.
- **Promote** a version to latest (goes live): `promote_character_version`. State which version is live now and which will be after.
- **Roll back** by promoting an older version, or reset the draft from a version with `fork_character_version` (replaces the current draft).
- **Revert one change** in the draft: `revert_character_draft_change`.
- **Discard** all unreleased draft changes: `discard_character_draft` (permanent for those edits).
- **Deprecate or restore** a version: `deprecate_character_version`.

`fork_character_version`, `discard_character_draft` and `promote_character_version` overwrite state - always call out what will be lost or replaced.

## Output

List versions newest first with the latest marked. After a write, re-run `list_character_versions` and report the new state.
