from pathlib import Path

import pytest

from src.services.entitlements_catalog import load_entitlements_catalog

pytestmark = pytest.mark.unit

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "policies"


def test_load_entitlements_catalog_reads_fixture_bundle():
    manifest = load_entitlements_catalog(FIXTURES_DIR)
    definitions = manifest.namespaces["ui"]

    assert manifest.namespace_names == ["ui"]
    assert [item.entity_id for item in definitions] == [
        'ui::Menu::"clinician"',
        'ui::Menu::"debug"',
        'ui::Menu::"operator"',
        'ui::Menu::"patient"',
    ]
    assert definitions[0].action == "View"
    assert definitions[0].key == definitions[0].resource


def test_load_entitlements_catalog_requires_cedar_files(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="No Cedar policy files"):
        load_entitlements_catalog(tmp_path)


def test_load_entitlements_catalog_requires_view_permits(tmp_path: Path):
    (tmp_path / "ui").mkdir()
    (tmp_path / "ui" / "empty.cedar").write_text(
        'permit (principal, action, resource);',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="No View permits on ui::"):
        load_entitlements_catalog(tmp_path)


def test_load_entitlements_catalog_rejects_duplicate_entities(tmp_path: Path):
    (tmp_path / "ui").mkdir()
    duplicate = """
permit (
    principal is ui::User,
    action == Action::"View",
    resource == ui::Menu::"operator"
) when { true };
"""
    (tmp_path / "ui" / "a.cedar").write_text(duplicate, encoding="utf-8")
    (tmp_path / "ui" / "b.cedar").write_text(duplicate, encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate UI entity"):
        load_entitlements_catalog(tmp_path)


def test_load_entitlements_catalog_ignores_non_view_permits(tmp_path: Path):
    (tmp_path / "ui").mkdir()
    (tmp_path / "ui" / "mixed.cedar").write_text(
        """
permit (
    principal is ui::User,
    action == Action::"Edit",
    resource == ui::Menu::"hidden"
) when { true };

permit (
    principal is ui::User,
    action == Action::"View",
    resource == ui::Menu::"visible"
) when { true };
""",
        encoding="utf-8",
    )

    manifest = load_entitlements_catalog(tmp_path)
    assert [item.entity_id for item in manifest.namespaces["ui"]] == ['ui::Menu::"visible"']
