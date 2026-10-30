#!/usr/bin/env python3
"""Release checks that the platform validators do not cover.

  python3 scripts/validate.py
  python3 scripts/validate.py --catalog \\
      ../convai-api-mcp/src/convai_api_mcp/data/operation-catalog.v1.json

Run `claude plugin validate packages/claude --strict`
and `claude plugin validate .` as well (CI does both).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_MCP_URL = "https://mcp-api.convai.com/mcp"
# Scopes that may be requested: the union of the MCP catalog's required and
# conditional scopes. knowledge-bank:write is conditional on character writes
# that touch knowledge associations (Character API enforces it).
PUBLISHED_SCOPES = {
    "character:read",
    "character:write",
    "backstory:generate",
    "chat-history:read",
    "knowledge-bank:read",
    "knowledge-bank:write",
}
SECRET = re.compile(
    r"cv(?:pat|oat|ort|oac)_[0-9a-f]{8,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|AIza[0-9A-Za-z_-]{30,}"
)
NON_PROD_HOST = re.compile(
    r"(?:-stg|-preview|-dev)\.convai\.com"
    r"|\blocalhost\b"
    r"|127\.0\.0\.1",
    re.I,
)
INTERNAL_REFERENCE = re.compile(
    r"convaixr\.atlassian\.net"
    r"|conv-ai\.slack\.com"
    r"|console\.cloud\.google\.com"
    r"|(?:[a-z0-9-]+\.)*internal\.convai\.com"
    r"|\bprj-cs-[a-z0-9-]+"
    r"|\bCORE-\d+\b",
    re.I,
)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)

errors: list[str] = []


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def public_documentation_errors(text: str) -> list[str]:
    """Keep private operational references out of the public entry point."""
    return [
        f"README.md: {message}"
        for pattern, message in (
            (SECRET, "looks like it contains a credential"),
            (NON_PROD_HOST, "references a non-production host"),
            (INTERNAL_REFERENCE, "references internal operational information"),
        )
        if pattern.search(text)
    ]


def schema_identifiers(node, found: set[str]) -> None:
    """Collect property, required and string enum or const names from a JSON schema."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "properties" and isinstance(value, dict):
                found.update(value)
            elif key == "required" and isinstance(value, list):
                found.update(v for v in value if isinstance(v, str))
            elif key in ("enum", "const"):
                values = value if isinstance(value, list) else [value]
                found.update(v for v in values if isinstance(v, str))
            schema_identifiers(value, found)
    elif isinstance(node, list):
        for item in node:
            schema_identifiers(item, found)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog",
        type=Path,
        help="convai-api-mcp operation-catalog.v1.json",
    )
    args = parser.parse_args()
    errors.extend(public_documentation_errors((ROOT / "README.md").read_text()))

    openai = load("packages/openai/plugin.json")
    claude = load("packages/claude/.claude-plugin/plugin.json")
    grok = load("packages/grok-bot/.cursor-plugin/plugin.json")
    cursor_market = load(".cursor-plugin/marketplace.json")
    market = load(".claude-plugin/marketplace.json")
    entry = next(
        (p for p in market["plugins"] if p["name"] == claude["name"]),
        None,
    )
    cases = load("shared/review-cases.json")

    # One product, one version everywhere.
    check(
        openai["name"] == claude["name"] == grok["name"],
        "plugin names differ between packages",
    )
    check(entry is not None, "marketplace does not list the Claude plugin")
    check(
        [p.get("source") for p in cursor_market.get("plugins", []) if p.get("name") == grok["name"]]
        == ["packages/grok-bot"],
        ".cursor-plugin/marketplace.json must list the Grok Bot plugin once, source packages/grok-bot",
    )
    versions = {
        openai["version"],
        claude["version"],
        grok["version"],
        market.get("version"),
        entry and entry.get("version"),
    }
    check(len(versions) == 1, f"versions differ: {sorted(map(str, versions))}")
    check(
        entry is None or entry["source"] == "./packages/claude",
        "marketplace source must be ./packages/claude",
    )
    for key in ("$schema", "name", "version", "description"):
        check(key in openai, f"packages/openai/plugin.json missing {key}")

    # Production endpoint only; scopes limited to what is published.
    for rel in (
        "packages/openai/mcp.json",
        "packages/claude/.mcp.json",
        "packages/grok-bot/mcp.json",
    ):
        if not (ROOT / rel).is_file():
            errors.append(
                f"{rel} is missing: the plugin would ship without "
                "the MCP server"
            )
            continue
        for name, server in load(rel)["mcpServers"].items():
            check(
                server.get("url") == PRODUCTION_MCP_URL,
                f"{rel}:{name} url must be {PRODUCTION_MCP_URL}",
            )
            if rel.startswith("packages/grok-bot/"):
                check(
                    server.get("auth", {}).get("CLIENT_ID") == "grok-bot",
                    f"{rel}:{name} auth.CLIENT_ID must be grok-bot (no DCR on Convai Auth)",
                )
            requested = set(server.get("scopes", []))
            requested |= set(server.get("auth", {}).get("scopes", []))
            extra = requested - PUBLISHED_SCOPES
            check(
                not extra,
                f"{rel}:{name} requests unpublished scopes {sorted(extra)}",
            )

    # Starter prompts and review cases.
    ui = (
        openai.get("extensions", {})
        .get("com.openai", {})
        .get("interface", {})
    )
    check(
        ui.get("defaultPrompt") == cases["starterPrompts"],
        "OpenAI defaultPrompt differs from "
        "shared/review-cases.json starterPrompts",
    )
    check(
        len(cases["positive"]) == 5,
        "OpenAI submission needs exactly 5 positive test cases",
    )
    check(
        len(cases["negative"]) == 3,
        "OpenAI submission needs exactly 3 negative test cases; keep extra cases in supplementalNegative",
    )
    # OpenAI portal limits.
    for key in ("displayName", "shortDescription"):
        check(0 < len(ui.get(key, "")) <= 30, f"OpenAI interface.{key} must be 1-30 characters")
    prompts = ui.get("defaultPrompt", [])
    check(0 < len(prompts) <= 3, "OpenAI defaultPrompt allows at most 3 prompts")
    check(all(len(p) <= 128 for p in prompts), "OpenAI defaultPrompt entries must be 128 characters or fewer")
    for key in ("privacyPolicyURL", "termsOfServiceURL", "websiteURL", "supportURL"):
        check(
            str(ui.get(key, "")).startswith("https://"),
            f"OpenAI interface.{key} must be an https URL",
        )

    # Brand assets referenced by the OpenAI listing must ship in the package.
    for key in ("logo", "composerIcon"):
        check(key in ui, f"OpenAI interface.{key} is missing")
    for key in ("logo", "composerIcon", "screenshots"):
        values = ui.get(key, [])
        for asset in values if isinstance(values, list) else [values]:
            check(
                str(asset).startswith("./")
                and (ROOT / "packages/openai" / asset).is_file(),
                f"OpenAI interface.{key} {asset!r} is not a file in packages/openai",
            )

    # Skills.
    tool_names = None
    if args.catalog:
        catalog = json.loads(args.catalog.read_text())
        # Skills also name tool arguments, result fields and enum values in
        # code spans; accept any identifier the catalog's tool and upstream
        # contract schemas define.
        tool_names = {t["toolName"] for t in catalog["tools"]}
        for tool in catalog["tools"]:
            schema_identifiers(tool.get("mcpInputSchema"), tool_names)
            schema_identifiers(tool.get("mcpOutputSchema"), tool_names)
        schema_identifiers(catalog.get("contracts"), tool_names)
    skills = sorted((ROOT / "shared" / "skills").glob("*/SKILL.md"))
    check(bool(skills), "no skills in shared/skills")
    for path in skills:
        text = path.read_text()
        match = FRONTMATTER.match(text)
        rel = path.relative_to(ROOT)
        if not match:
            errors.append(f"{rel}: missing --- frontmatter ---")
            continue
        fields = dict(
            line.split(":", 1)
            for line in match.group(1).splitlines()
            if ":" in line
        )
        name = fields.get("name", "").strip()
        description = fields.get("description", "").strip()
        check(
            name == path.parent.name,
            f"{rel}: name must equal directory name",
        )
        check(
            0 < len(description) <= 1024,
            f"{rel}: description must be 1-1024 characters",
        )
        if tool_names is not None:
            for tool in set(re.findall(r"`([a-z]+(?:_[a-z]+)+)`", text)):
                check(
                    tool in tool_names,
                    f"{rel}: `{tool}` is not a tool or schema field in the MCP catalog",
                )

    # Nothing shipped may carry credentials or non-production endpoints.
    for pkg in ("packages", "shared", ".claude-plugin"):
        for path in (ROOT / pkg).rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(errors="ignore")
            rel = path.relative_to(ROOT)
            check(
                not SECRET.search(text),
                f"{rel}: looks like it contains a credential",
            )
            check(
                not NON_PROD_HOST.search(text),
                f"{rel}: references a non-production host",
            )

    for message in errors:
        print(f"error: {message}", file=sys.stderr)
    if not errors:
        print(
            f"ok: {claude['name']} {claude['version']} ({len(skills)} skills)"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
