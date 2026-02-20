#!/usr/bin/env python3
"""
Fling project initializer — Python equivalent of src/cli/commands/init.ts.

Scaffolds a new Fling project from the bundled template directory.
Uses dependency injection for testability.
"""

import json
import os
import secrets
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Optional

RANDOM_CODE_CHARSET = "23456789abcdefghjkmnpqrstuvwxyz"
RANDOM_CODE_LENGTH = 6
SECRETS_HEADER = "# Fling secrets\n# Format: KEY=value\n"


@dataclass
class InitDeps:
    """Injectable dependencies for the init process."""

    copy_tree: Callable[[str, str], None]
    copy_file: Callable[[str, str], None]
    listdir: Callable[[str], List[str]]
    isdir: Callable[[str], bool]
    makedirs: Callable[[str, bool], None]
    write_file: Callable[[str, str], None]
    read_file: Callable[[str], str]
    chmod: Callable[[str, int], None]
    getcwd: Callable[[], str]
    get_random_bytes: Callable[[int], bytes]
    get_npm_version: Callable[[], Optional[str]]


def create_default_deps() -> InitDeps:
    """Create real implementations of all dependencies."""

    def _copy_tree(src: str, dst: str) -> None:
        shutil.copytree(src, dst)

    def _copy_file(src: str, dst: str) -> None:
        shutil.copy2(src, dst)

    def _listdir(path: str) -> List[str]:
        return os.listdir(path)

    def _isdir(path: str) -> bool:
        return os.path.isdir(path)

    def _makedirs(path: str, exist_ok: bool = True) -> None:
        os.makedirs(path, exist_ok=exist_ok)

    def _write_file(path: str, content: str) -> None:
        with open(path, "w") as f:
            f.write(content)

    def _read_file(path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    def _chmod(path: str, mode: int) -> None:
        os.chmod(path, mode)

    def _get_random_bytes(n: int) -> bytes:
        return secrets.token_bytes(n)

    def _get_npm_version() -> Optional[str]:
        try:
            result = subprocess.run(
                ["npm", "view", "flingit", "version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    return InitDeps(
        copy_tree=_copy_tree,
        copy_file=_copy_file,
        listdir=_listdir,
        isdir=_isdir,
        makedirs=_makedirs,
        write_file=_write_file,
        read_file=_read_file,
        chmod=_chmod,
        getcwd=os.getcwd,
        get_random_bytes=_get_random_bytes,
        get_npm_version=_get_npm_version,
    )


def generate_project_id(get_random_bytes: Callable[[int], bytes]) -> str:
    """Generate a 6-character project ID using the safe charset."""
    raw = get_random_bytes(RANDOM_CODE_LENGTH)
    return "".join(
        RANDOM_CODE_CHARSET[b % len(RANDOM_CODE_CHARSET)] for b in raw
    )


def run_init(dest: str, deps: InitDeps) -> None:
    """Initialize a Fling project at the given destination directory."""
    # 1. Resolve template path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "..", "template")
    template_dir = os.path.normpath(template_dir)

    if not deps.isdir(template_dir):
        print(
            f"Error: Template directory not found at {template_dir}. "
            "Was the plugin built? Run: npm run build:plugin",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Check directory is empty
    try:
        entries = deps.listdir(dest)
    except OSError as e:
        print(f"Error: Cannot read directory {dest}: {e}", file=sys.stderr)
        sys.exit(1)

    if entries:
        first_few = ", ".join(sorted(entries)[:5])
        print(
            f"Error: Directory is not empty: {dest}. "
            f"Found {len(entries)} entries: {first_few}. "
            "Create an empty directory first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 3. Copy template entries
    print("Copying template files...", end=" ", flush=True)
    try:
        template_entries = deps.listdir(template_dir)
    except OSError as e:
        print(f"\nError: Cannot read template directory: {e}", file=sys.stderr)
        sys.exit(1)

    for entry in template_entries:
        src_path = os.path.join(template_dir, entry)
        dest_name = "." + entry[4:] if entry.startswith("dot-") else entry
        dest_path = os.path.join(dest, dest_name)
        try:
            if deps.isdir(src_path):
                deps.copy_tree(src_path, dest_path)
            else:
                deps.copy_file(src_path, dest_path)
        except Exception as e:
            print(
                f"\nError: Failed to copy template entry '{entry}': {e}. "
                "The project may be in a partial state — remove contents and retry.",
                file=sys.stderr,
            )
            sys.exit(1)
    print("done")

    # 4. Rename dot-prefixed entries (handled inline above during copy)
    print("Renaming dot-prefixed entries... done")

    # 5. Read and modify package.json
    print("Configuring package.json...", end=" ", flush=True)
    package_json_path = os.path.join(dest, "package.json")
    try:
        package_json_content = deps.read_file(package_json_path)
    except FileNotFoundError:
        print(
            "\nError: package.json not found after copying template — "
            "template may be corrupt",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        package_json = json.loads(package_json_content)
    except json.JSONDecodeError as e:
        print(f"\nError: Failed to parse package.json: {e}", file=sys.stderr)
        sys.exit(1)

    project_name = os.path.basename(dest) or "fling-project"
    package_json["name"] = project_name

    # 6. Fetch latest flingit version
    print("done")
    print("Fetching latest flingit version...", end=" ", flush=True)
    npm_version = deps.get_npm_version()
    if npm_version:
        dep_version = f"^{npm_version}"
        print(f"done (v{npm_version})")
    else:
        dep_version = package_json.get("dependencies", {}).get(
            "flingit", "^0.0.1"
        )
        print(f"failed (using fallback {dep_version})")
        print(
            f"Warning: Failed to fetch latest flingit version from npm. "
            f"Using fallback version {dep_version}. "
            "Make sure npm is installed and you have internet access.",
            file=sys.stderr,
        )

    dependencies = package_json.get("dependencies", {})
    dependencies.pop("fling", None)
    dependencies["flingit"] = dep_version
    package_json["dependencies"] = dependencies

    # 7. Generate project ID
    try:
        project_id = generate_project_id(deps.get_random_bytes)
    except Exception as e:
        print(f"Error: Failed to generate project ID: {e}", file=sys.stderr)
        sys.exit(1)

    package_json["fling"] = {"projectName": project_id}

    try:
        deps.write_file(
            package_json_path, json.dumps(package_json, indent=2) + "\n"
        )
    except Exception as e:
        print(f"\nError: Failed to write package.json: {e}", file=sys.stderr)
        sys.exit(1)

    # 8. Create .fling/data directory
    print("Creating project directories...", end=" ", flush=True)
    try:
        deps.makedirs(os.path.join(dest, ".fling", "data"), True)
    except Exception as e:
        print(
            f"\nError: Failed to create .fling/data directory: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    print("done")

    # 9. Create secrets file
    print("Creating secrets file...", end=" ", flush=True)
    secrets_path = os.path.join(dest, ".fling", "secrets")
    try:
        deps.write_file(secrets_path, SECRETS_HEADER)
        deps.chmod(secrets_path, 0o600)
    except Exception as e:
        print(
            f"\nError: Failed to create .fling/secrets: {e}", file=sys.stderr
        )
        sys.exit(1)
    print("done")

    print("\nFling project initialized successfully.")


def main() -> None:
    deps = create_default_deps()
    dest = deps.getcwd()
    run_init(dest, deps)


if __name__ == "__main__":
    main()
