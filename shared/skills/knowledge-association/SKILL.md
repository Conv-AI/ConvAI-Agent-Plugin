---
name: knowledge-association
description: See which Convai knowledge bank documents a character uses and connect or disconnect existing documents. Use when the user asks what a character knows, which documents are attached, or to add or remove an existing knowledge document from a character.
---

# Manage a character's knowledge documents

This skill links existing documents to characters. It cannot upload, edit or delete documents - point the user to the Convai dashboard (https://convai.com/dashboard) for that.

## Workflow

1. Resolve the character (`list_characters` / `get_character`) and state its name and ID.
2. Call `list_knowledge_documents` for the character. Show each document's name, ID, status and whether it is connected.
3. **Connect**: confirm the document and character, then call `connect_knowledge_document`. Only use a retrieval mode the user chose.
4. **Disconnect**: confirm, then call `disconnect_knowledge_document`. The document itself is kept.
5. Re-list to confirm the result.

## Notes

- Documents still processing may not be usable yet; report their status rather than retrying.
- If the knowledge bank is not available for the account's plan, say so plainly.
