"""The single-file example must keep working, or it silently rots.

It is documentation people copy, so it gets the same checks as the package.
"""

import importlib.util
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_plugin import FakeContext  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# A single-file plugin lives at the repository root, which is where the release
# workflow and the registry expect to find it.
EXAMPLE = os.path.join(ROOT, "my_single_file_plugin.py")
WORKFLOWS = os.path.join(ROOT, "examples", "single_file")


@pytest.fixture
def example():
    spec = importlib.util.spec_from_file_location("my_single_file_plugin", EXAMPLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module


def test_the_example_sits_at_the_repository_root():
    """Where a single-file plugin belongs: next to the workflows that ship it."""
    assert os.path.isfile(EXAMPLE)
    assert os.path.dirname(EXAMPLE) == ROOT


def test_importing_it_needs_no_qt(example):
    """The Qt import is deferred, so scanners and tests can import the module."""
    assert example.PLUGIN_NAME


def test_metadata_matches_the_registry_contract(example):
    for name in ("PLUGIN_NAME", "PLUGIN_VERSION", "PLUGIN_AUTHOR", "PLUGIN_DESCRIPTION"):
        assert getattr(example, name, "").strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", example.PLUGIN_VERSION)


def test_it_has_no_run_attribute(example):
    """Same rule as the package: a module-level run() duplicates the menu entry."""
    assert not hasattr(example, "run")
    assert not hasattr(example, "autorun")


def test_initialize_registers_one_entry_and_the_handlers(example):
    context = FakeContext()
    example.initialize(context)
    assert len(context.menu_actions) == 1
    assert len(context.save_handlers) == 1
    assert len(context.load_handlers) == 1
    assert len(context.reset_handlers) == 1


def test_save_handler_is_silent_until_used(example):
    context = FakeContext()
    example.initialize(context)
    assert context.save_handlers[0]() == {}


def test_load_and_reset_round_trip(example):
    context = FakeContext()
    example.initialize(context)
    context.load_handlers[0]({"settings": {"repeat": 3}})
    assert example.current_settings["repeat"] == 3
    context.reset_handlers[0]()
    assert example.current_settings == example.get_default_settings()


def test_build_text_is_pure_logic(example):
    assert example.build_text({"greeting": "Hi", "repeat": 3}) == "Hi\nHi\nHi\n"
    assert example.build_text({}) == "Hello\n"
    assert example.build_text({"greeting": "x", "repeat": 0}) == "x\n"


def test_release_workflow_targets_the_script():
    """The example workflow must attach the .py, not a zip that does not exist."""
    path = os.path.join(WORKFLOWS, "release.yml")
    text = open(path, encoding="utf-8").read()
    assert "my_single_file_plugin.py" in text
    # The word "zip" appears in a comment explaining there is nothing to zip;
    # what must not appear is an actual zip step or a .zip asset.
    assert ".zip" not in text
    assert "zip -r" not in text
