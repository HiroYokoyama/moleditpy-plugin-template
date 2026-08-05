# MoleditPy Plugin Template

A starting point for a **third-party [MoleditPy](https://github.com/HiroYokoyama/python_molecular_editor)
plugin**: a working example plugin, a headless test suite, an API compatibility
check against the host, and a tag-driven release workflow.

Click **Use this template** on GitHub, then work through the checklist below.

## What you get

| Path | What it is |
|---|---|
| `my_plugin/__init__.py` | Metadata the registry reads, `initialize(context)`, and the three session handlers |
| `my_plugin/main_dialog.py` | A small dialog wired the way the host expects |
| `tests/test_plugin.py` | Metadata + registration tests (keep these — they catch the usual mistakes) |
| `tests/test_dialog.py` | Real-PyQt6 dialog tests, offscreen |
| `tests/test_api.py` + `plugin_api_checker.py` | Fails if you touch a host attribute that does not exist |
| `.github/workflows/test.yml` | CI on Linux + Windows, Python 3.11 and 3.13 |
| `.github/workflows/release.yml` | `v*.*.*` tag → zip → GitHub release |
| `.moleditpy-api-allowlist` | Escape hatch for host attributes the checker cannot see |

## Getting started

1. **Rename the package.** `my_plugin/` → your plugin's name (snake_case). Update
   the same name in both workflow files and in the test imports.
2. **Edit the metadata** at the top of `my_plugin/__init__.py`. `PLUGIN_VERSION`
   must be semver — the release workflow refuses a tag that does not match it.
3. **Pick one entry point.** A plugin that defines `run()` is auto-registered in
   the Plugin menu, so calling `add_menu_action()` as well produces a duplicate.
4. **Write your plugin**, keeping `PLUGIN_DEPENDENCIES` to packages the host does
   *not* already ship (PyQt6, rdkit and numpy are the host's).
5. **Run the tests** (below) and keep them green.

```bash
python -m pytest tests/ -v
```

To make the API check actually run, clone the main app next to your repo:

```bash
git clone --depth 1 https://github.com/HiroYokoyama/python_molecular_editor.git ..
```

Without it that test **skips** rather than fails, which is easy to miss — CI
clones it for you.

## Releasing

```bash
git tag v0.1.0        # must equal PLUGIN_VERSION
git push origin v0.1.0
```

The workflow verifies the tag against `PLUGIN_VERSION`, zips the package
(README and LICENSE included) and creates the GitHub release with
`my_plugin_0.1.0.zip` attached. Users can install that zip directly through the
MoleditPy Plugin Manager.

Watch CI go green **before** tagging: a tag cannot be un-released cleanly.

## Getting into the plugin registry

Listing your plugin in the
[registry](https://github.com/HiroYokoyama/moleditpy-plugins) is a **separate,
manual step, and it is not automated for third-party repos**. The registry
updates itself from a repository dispatch that needs a `REGISTRY_PAT` secret,
which only the registry maintainer can issue.

The release workflow tries the dispatch **only if that secret exists** on your
repository: maintainers get automatic registration, everyone else gets a no-op
plus a log line pointing at the manual route. Nothing fails either way.

So, after your release is published:

1. Open a **Request Plugin Registration / Update** issue on the registry repo:
   <https://github.com/HiroYokoyama/moleditpy-plugins/issues/new/choose>
2. Fill in the release asset URL, e.g.
   `https://github.com/<you>/<repo>/releases/download/v0.1.0/my_plugin_0.1.0.zip`,
   and the asset's SHA-256 (the form asks for it, and registration verifies it):
   - PowerShell: `Get-FileHash ./my_plugin_0.1.0.zip -Algorithm SHA256`
   - bash: `shasum -a 256 my_plugin_0.1.0.zip`
3. A maintainer runs the registration script against that URL, which reads your
   `PLUGIN_*` constants and records the hash.

For later versions, open an issue again with the new release URL (or ask to be
granted the dispatch secret if you release often).

## Conventions worth keeping

- **Do not write to the user's project until your dialog is actually used** —
  the save handler returns `{}` until then.
- **Guard every host call.** Wrap `context.*` access that may not exist in older
  hosts with `hasattr`, and add it to `.moleditpy-api-allowlist` with a reason.
- **Never block on a modal dialog during construction** — it deadlocks headless
  CI and startup.
- **Write files with `newline="\n"`** so output is identical on every platform.
- **Ship no secrets.** Nothing in this template needs a token; the release
  workflow uses only the automatic `GITHUB_TOKEN`.

## Licence

This template is GPL-3.0 (see [LICENSE](LICENSE)), matching the MoleditPy
ecosystem. Replace it if your plugin uses a different licence.
