""" Build the landing page hero project and write its real output into the website sources.

The hero shows a Python snippet beside the files StewBeet generates from it. Both used to be
hand-written constants that had already drifted from reality, so this script builds
docs/web/playground/hero for real and records what came out.

docs/web/src/components/heroTree.json stays hand-curated, because the real paths are far too long
to read in half a hero panel, but every one of its leaves carries the exact build path it stands
for. This script fails when a leaf points at a file the build did not produce, which is what keeps
the curated tree honest.

Run `uv run scripts/build_hero_output.py` after touching the hero project, and `--check` in CI.
"""
# Imports
import argparse
import difflib
import io
import json
import os
import shutil
import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import stouputils as stp
from beet import run_beet

# Constants
ROOT: str = stp.get_root_path(__file__, go_up=2)
""" Repository root: this script lives in python_package/scripts/. """

PROJECT: str = f"{ROOT}/docs/web/playground/hero"
""" The real StewBeet project behind the hero. """

TREE_PATH: str = f"{ROOT}/docs/web/src/components/heroTree.json"
""" Hand-curated display tree whose leaves carry the real build path they stand for. """

META_PATH: str = f"{ROOT}/docs/web/src/generated/heroOutput.json"
""" Small file the landing page imports statically: the tree plus per-leaf metadata. """

CONTENTS_PATH: str = f"{ROOT}/docs/web/src/generated/heroContents.json"
""" Text bodies, imported dynamically so they never land in the landing page bundle. """

IMAGES_DIR: str = f"{ROOT}/docs/web/public/generated/hero"
""" Generated PNGs, served as real files rather than inlined as data URLs. """


# Functions
def dump_pack(pack: Any, prefix: str) -> dict[str, bytes]:
    """ Serialize a pack to the exact paths and bytes it would have written to disk.

    Going through a ZipFile in memory rather than `output: build` keeps the build side effect free
    and still goes through beet's own dump path, so what is recorded is what a user would get.

    Args:
        pack   (Any): The beet pack to serialize (`ctx.data` or `ctx.assets`).
        prefix (str): Folder the pack would have been written to, ex: "datapack".
    Returns:
        dict[str, bytes]: Mapping of build-relative path to file content.
    """
    buffer: io.BytesIO = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        pack.dump(archive)
    with ZipFile(buffer) as archive:
        return {f"{prefix}/{name}": archive.read(name) for name in archive.namelist()}


def build_hero_project() -> dict[str, bytes]:
    """ Run the hero project and return every file it generated.

    `cache=True` looks like a detail but is load bearing: with the default `cache=False` beet runs
    the whole build inside a temporary directory, and the project's relative `textures_folder`
    then resolves against the wrong place. The CLI sidesteps this by chdir-ing in
    `get_project_config`, so this does the same.

    Returns:
        dict[str, bytes]: Mapping of build-relative path to file content.
    """
    os.chdir(PROJECT)
    sys.path.insert(0, PROJECT)
    with run_beet(config=f"{PROJECT}/beet.yml", directory=PROJECT, cache=True) as ctx:
        return dump_pack(ctx.data, "datapack") | dump_pack(ctx.assets, "resource_pack")


def iter_leaves(nodes: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """ Walk the curated tree and yield every file node, in display order.

    Args:
        nodes (list[dict[str, Any]]): Nodes to walk.
    Returns:
        Iterator[dict[str, Any]]: Every node without children.
    """
    for node in nodes:
        if children := node.get("children"):
            yield from iter_leaves(children)
        else:
            yield node


def validate(leaves: list[dict[str, Any]], built: dict[str, bytes]) -> None:
    """ Stop the build when the curated tree no longer matches what StewBeet produced.

    Args:
        leaves (list[dict[str, Any]]): Every leaf of the curated tree.
        built  (dict[str, bytes]):     Everything the build generated.
    """
    errors: list[str] = []
    if not leaves:
        errors.append("The curated tree has no files at all.")

    seen: set[str] = set()
    for leaf in leaves:
        path: str = leaf.get("path", "")
        if not path:
            errors.append(f"Leaf {leaf.get('name', '?')!r} has no 'path'.")
        elif path in seen:
            errors.append(f"Path {path!r} is listed twice.")
        elif path not in built:
            close: list[str] = difflib.get_close_matches(path, built.keys(), n=5, cutoff=0.5)
            suggestions: str = "\n".join(f"        {match}" for match in close) or "        (nothing similar)"
            errors.append(f"Path {path!r} was not generated. Closest real paths:\n{suggestions}")
        seen.add(path)

    if errors:
        stp.error(f"heroTree.json does not match the build ({len(errors)} problem(s)):")
        for message in errors:
            stp.error(f"  - {message}")
        sys.exit(1)


def collect_outputs(tree: list[dict[str, Any]], built: dict[str, bytes]) -> tuple[dict[str, Any], dict[str, str], dict[str, bytes]]:
    """ Split the build into the three artifacts the website consumes.

    Args:
        tree  (list[dict[str, Any]]): The curated tree, enriched in place with per-leaf metadata.
        built (dict[str, bytes]):     Everything the build generated.
    Returns:
        tuple: The metadata document, the text bodies by path, and the PNG bytes by slug.
    """
    contents: dict[str, str] = {}
    images: dict[str, bytes] = {}

    leaves: list[dict[str, Any]] = list(iter_leaves(tree))
    for leaf in leaves:
        path: str = leaf["path"]
        data: bytes = built[path]
        try:
            text: str = data.decode("utf-8")
        except UnicodeDecodeError:
            slug: str = path.replace("/", "__")
            leaf["kind"] = "image"
            leaf["bytes"] = len(data)
            leaf["url"] = f"/generated/hero/{slug}"
            images[slug] = data
        else:
            # A build writes CRLF on Windows and LF on Linux. Normalizing makes this file identical
            # on both, without which CI would rebuild it and see every line as changed. It also
            # matters on screen: a stray CR inside the <pre> the panel builds is a line break of
            # its own, on top of the newline between rows, so every line renders double spaced.
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            leaf["kind"] = "text"
            leaf["bytes"] = len(text.encode("utf-8"))
            leaf["lines"] = text.count("\n") + 1
            contents[path] = text

    meta: dict[str, Any] = {
        "generatedAt": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stewbeetVersion": version("stewbeet"),
        "fileCount": len(leaves),
        "tree": tree,
    }
    return meta, contents, images


def as_json(document: Any) -> str:
    """ Serialize the way the other generated files in docs/web are serialized.

    Args:
        document (Any): Anything JSON serializable.
    Returns:
        str: Indented JSON with a trailing newline.
    """
    return f"{json.dumps(document, indent=4, ensure_ascii=False)}\n"


def write_outputs(meta: dict[str, Any], contents: dict[str, str], images: dict[str, bytes]) -> None:
    """ Write the three artifacts, removing PNGs the tree no longer references.

    Args:
        meta     (dict[str, Any]):   The metadata document.
        contents (dict[str, str]):   Text bodies by path.
        images   (dict[str, bytes]): PNG bytes by slug.
    """
    # newline="" keeps the "\n" as written: the default would turn them into CRLF on Windows and
    # the committed files would then flip wholesale the first time someone regenerates on Linux.
    Path(META_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(META_PATH).write_text(as_json(meta), encoding="utf-8", newline="")
    Path(CONTENTS_PATH).write_text(as_json(contents), encoding="utf-8", newline="")

    shutil.rmtree(IMAGES_DIR, ignore_errors=True)
    Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    for slug, data in images.items():
        Path(f"{IMAGES_DIR}/{slug}").write_bytes(data)


def check_outputs(meta: dict[str, Any], contents: dict[str, str], images: dict[str, bytes]) -> None:
    """ Fail when the committed artifacts are not what a fresh build produces.

    `generatedAt` is ignored: it changes on every run and would make the check always fail.

    Args:
        meta     (dict[str, Any]):   The freshly built metadata document.
        contents (dict[str, str]):   Freshly built text bodies by path.
        images   (dict[str, bytes]): Freshly built PNG bytes by slug.
    """
    problems: list[str] = []

    for path, fresh in ((META_PATH, meta), (CONTENTS_PATH, contents)):
        if not Path(path).exists():
            problems.append(f"{stp.relative_path(path)} is missing.")
            continue
        committed: Any = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(fresh, dict) and "generatedAt" in fresh:
            committed = {**committed, "generatedAt": fresh["generatedAt"]}
        if committed != fresh:
            diff: str = "\n".join(difflib.unified_diff(
                as_json(committed).splitlines(),
                as_json(fresh).splitlines(),
                fromfile=f"committed/{Path(path).name}",
                tofile=f"rebuilt/{Path(path).name}",
                lineterm="",
            ))
            problems.append(f"{stp.relative_path(path)} is out of date:\n{diff}")

    committed_images: set[str] = {p.name for p in Path(IMAGES_DIR).glob("*")} if Path(IMAGES_DIR).is_dir() else set()
    if committed_images != set(images):
        problems.append(f"{stp.relative_path(IMAGES_DIR)} holds {sorted(committed_images)}, expected {sorted(images)}.")
    else:
        for slug, data in images.items():
            if Path(f"{IMAGES_DIR}/{slug}").read_bytes() != data:
                problems.append(f"{stp.relative_path(IMAGES_DIR)}/{slug} differs from the build.")

    if problems:
        stp.error("The generated hero output is out of date. Run 'uv run scripts/build_hero_output.py'.")
        for message in problems:
            stp.error(f"  - {message}")
        sys.exit(1)
    stp.info("Hero output is up to date.")


# Main
@stp.measure_time(printer=stp.info, message="Hero output finished")
def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the committed output is stale, instead of rewriting it.")
    parser.add_argument("--list", action="store_true", help="Print every path the build produced and exit. Useful when editing heroTree.json.")
    args: argparse.Namespace = parser.parse_args()

    tree: list[dict[str, Any]] = json.loads(Path(TREE_PATH).read_text(encoding="utf-8"))
    built: dict[str, bytes] = build_hero_project()

    if args.list:
        for path in sorted(built):
            stp.info(f"{len(built[path]):>8}  {path}")
        stp.info(f"{len(built)} files generated.")
        return

    validate(list(iter_leaves(tree)), built)
    meta, contents, images = collect_outputs(tree, built)

    if args.check:
        check_outputs(meta, contents, images)
    else:
        write_outputs(meta, contents, images)
        stp.info(f"Wrote {meta['fileCount']} files ({len(contents)} text, {len(images)} image) from a {len(built)} file build.")


if __name__ == "__main__":
    main()
