#!/usr/bin/env python3
"""Copy shared/skills into every platform package.

  python3 scripts/build.py          # sync skills from shared/skills
  python3 scripts/build.py --check  # fail if a package's skills drifted
  python3 scripts/build.py --zip    # write dist/<platform>-<version>.zip
  python3 scripts/build.py \\
      --mcp-url https://mcp-api-preview.convai.com/mcp \\
      --out dist/preview
      # test build pointing at another MCP endpoint
"""
import argparse
import filecmp
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared" / "skills"
PACKAGES = {
    "openai": ROOT / "packages" / "openai",
    "claude": ROOT / "packages" / "claude",
}
MCP_FILES = {"openai": "mcp.json", "claude": ".mcp.json"}


def drifted(a: Path, b: Path) -> bool:
    if not b.is_dir():
        return True
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    return any(drifted(a / d, b / d) for d in cmp.common_dirs)


def sync(dest: Path) -> None:
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(SHARED, dest)


def version() -> str:
    plugin = PACKAGES["openai"] / "plugin.json"
    return json.loads(plugin.read_text())["version"]


def zip_dir(src: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(src))
    print(f"wrote {target.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--mcp-url")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.check:
        bad = [
            name
            for name, pkg in PACKAGES.items()
            if drifted(SHARED, pkg / "skills")
        ]
        if bad:
            print(
                "skills drifted from shared/skills in: "
                f"{', '.join(bad)}; run scripts/build.py",
                file=sys.stderr,
            )
            return 1
        print("skills in sync")
        return 0

    for pkg in PACKAGES.values():
        sync(pkg / "skills")
    print("synced skills into packages/openai and packages/claude")

    if args.mcp_url:
        out = (args.out or ROOT / "dist" / "custom").resolve()
        for name, pkg in PACKAGES.items():
            target = out / name
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(pkg, target)
            mcp_path = target / MCP_FILES[name]
            mcp = json.loads(mcp_path.read_text())
            for server in mcp["mcpServers"].values():
                server["url"] = args.mcp_url
            mcp_path.write_text(json.dumps(mcp, indent=2) + "\n")
        print(f"wrote test packages for {args.mcp_url} to {out}")

    if args.zip:
        for name, pkg in PACKAGES.items():
            archive = f"convai-character-authoring-{name}-{version()}.zip"
            zip_dir(pkg, ROOT / "dist" / archive)
    return 0


if __name__ == "__main__":
    sys.exit(main())
