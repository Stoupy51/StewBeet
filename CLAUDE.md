# StewBeet

Python package in `python_package`, docs in `docs`, project templates in `templates`.

## Conventions

- When beet misbehaves or is slow, patch it from `stewbeet/plugins/initialize/beet_patches.py`, never in `forks/beet`: the fork stays pullable from upstream only while its diff is near empty. One function per patch, named like the upstream one with a prefix, a docstring saying what upstream does and why it is replaced, and `PATCHES_APPLIED` guarding re-entry so `stewbeet watch` never wraps a method twice.
- A module-level state or `stp.simple_cache` that depends on `Mem` or the context, or has side effects, leaks across `stewbeet watch` cycles. Make it per-instance, or clear it in `plugins/initialize/__init__.py`.
- Welds run through `run_weld(cache=ProjectCache(temp))`. Never `cache=False` (beet changes directory into a temp folder and threads race), never the weld CLI (its shared cache breaks concurrent builds).

## Verify

- Builds are deterministic. After `stewbeet rebuild` only zip entry timestamps change, so compare name to CRC maps of the zips, not raw bytes. Test on `templates/extensive`, `SimplEnergy` and `StardustFragment`.
- Docs: `py -m sphinx -b html docs/source <tmp> -q` from the repo root. A module whose annotations use an `if TYPE_CHECKING:` import starts with `from __future__ import annotations`. No `Attributes:` section in a class docstring, document each field under it (`__slots__` as a dict). Docstrings are reST: `.. code-block:: python`, a blank line before `Args:`.
