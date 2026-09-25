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
    r"|localhost(?!:8080\b)"
    r"|127\.0\.0\.1"
)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)

errors: list[str] = []


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog",
        type=Path,
        help="convai-api-mcp operation-catalog.v1.json",
    )
    args = parser.parse_args()

    openai = load("packages/openai/plugin.json")
    claude = load("packages/claude/.claude-plugin/plugin.json")
    market = load(".claude-plugin/marketplace.json")
    entry = next(
        (p for p in market["plugins"] if p["name"] == claude["name"]),
        None,
    )
    cases = load("shared/review-cases.json")

    # One product, one version everywhere.
    check(
        openai["name"] == claude["name"],
        "plugin names differ between packages",
    )
    check(entry is not None, "marketplace does not list the Claude plugin")
    versions = {
        openai["version"],
        claude["version"],
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
    for rel in ("packages/openai/mcp.json", "packages/claude/.mcp.json"):
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
            extra = set(server.get("scopes", [])) - PUBLISHED_SCOPES
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
        len(cases["positive"]) >= 5,
        "OpenAI review needs at least 5 positive test cases",
    )
    check(
        len(cases["negative"]) >= 3,
        "OpenAI review needs at least 3 negative test cases",
    )
    for key in ("privacyPolicyURL", "termsOfServiceURL", "websiteURL"):
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
        tool_names = {t["toolName"] for t in catalog["tools"]}
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
                    f"{rel}: `{tool}` is not a tool in the MCP catalog",
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
