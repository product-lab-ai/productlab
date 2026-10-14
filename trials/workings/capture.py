"""Copy the current Workings source without changing or cleaning its checkout."""

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def source_manifest(root):
    names = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    files = {}
    for name in sorted(set(names.decode().split("\0")) - {""}):
        path = root / name
        if path.is_symlink():
            raise ValueError(f"Source symlinks need explicit review: {name}")
        if not path.exists():
            continue
        if not path.is_file():
            raise ValueError(f"Unsupported source entry: {name}")
        files[name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "executable": bool(path.stat().st_mode & 0o111),
        }
    return files


def capture(source, output):
    source, output = source.resolve(), output.resolve()
    if output == source or output.is_relative_to(source):
        raise ValueError("Keep the review outside the source checkout")
    before = source_manifest(source)
    if not before:
        raise ValueError("The source checkout has no files to capture")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    copy = output / "source"
    copy.mkdir()
    record = {
        "status": "copying",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "head": git(source, "rev-parse", "HEAD").decode().strip(),
        "branch": git(source, "branch", "--show-current").decode().strip(),
        "worktree_status": git(source, "status", "--porcelain").decode(),
        "files": before,
    }
    manifest = output / "source-manifest.json"
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    try:
        for name, expected in before.items():
            target = copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target, follow_symlinks=False)
            if (
                target.is_symlink()
                or hashlib.sha256(target.read_bytes()).hexdigest() != expected["sha256"]
            ):
                raise ValueError(f"Source changed while copying: {name}")
        if source_manifest(source) != before:
            raise ValueError("Source changed during capture; keep this failed copy as evidence")
        record["status"] = "verified"
    except Exception as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        manifest.write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = capture(args.source, args.output)
    print(f"Verified {len(record['files'])} source files in {args.output}")


if __name__ == "__main__":
    main()
