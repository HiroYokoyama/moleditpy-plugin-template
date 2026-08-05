# Single-file plugin

Most plugins in the registry are a single `.py` file rather than a package.
This folder is a complete, working example of that shape, plus the workflow
changes it needs.

| File | What to do with it |
|---|---|
| `../../my_single_file_plugin.py` | The plugin itself, at the repository root where this shape belongs. Rename it. |
| `release.yml` | Copy to `.github/workflows/release.yml` — it attaches the `.py` instead of a zip. |
| `test.yml` | Copy to `.github/workflows/test.yml` — same as the package version with the coverage target changed. |

The example is not decoration: the repository's own test suite imports it and
exercises `initialize()`, so it cannot drift out of date.

## What differs from the package layout

* **Release asset.** There is nothing to zip; the script itself is attached, and
  registration accepts a `.py` URL exactly as it accepts a `.zip`.
* **No `settings.json` beside the code.** The package template keeps one next to
  `__init__.py`; a loose script should persist through the save/load handlers
  instead, so a user's project carries its own state.
* **Qt imported inside the function.** Keeping the Qt import inside
  `_make_dialog()` means importing the module (as the tests and the registry
  scanner do) never needs a GUI toolkit.

Everything else is identical — the same metadata constants, the same
`initialize(context)` contract, the same rule that a module-level `run()` makes
the host add its own Plugins-menu entry.

## When to prefer a package

Once you want more than one module — a parser, a writer, a worker thread — the
package layout in `my_plugin/` is easier to test and to read. Converting later
is mechanical: move the file into a folder as `__init__.py` and split from there.

A real single-file plugin to compare against:
[`3d_molecule_on_2d`](https://github.com/HiroYokoyama/moleditpy_3d-molecule-on-2d).
