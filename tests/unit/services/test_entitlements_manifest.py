import json
from pathlib import Path

import pytest

from src.services.entitlements_manifest import load_entitlements_manifest

pytestmark = pytest.mark.unit

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "policies"


def test_load_entitlements_manifest_reads_fixture_bundle():
    manifest = load_entitlements_manifest(FIXTURES_DIR)
    definitions = manifest.namespaces["ui"]

    assert manifest.namespace_names == ["ui"]
    assert [item.key for item in definitions] == [
        "ui:menu:operator",
        "ui:menu:debug",
        "ui:menu:patient",
        "ui:menu:clinician",
    ]
    assert definitions[0].resource == 'ui::Menu::"operator"'
    assert definitions[0].action == "View"


def test_load_entitlements_manifest_requires_manifest_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="entitlements.json"):
        load_entitlements_manifest(tmp_path)


def test_load_entitlements_manifest_rejects_empty_namespaces(tmp_path: Path):
    manifest_path = tmp_path / "entitlements.json"
    manifest_path.write_text(json.dumps({"namespaces": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="non-empty 'namespaces' object"):
        load_entitlements_manifest(tmp_path)


def test_load_entitlements_manifest_rejects_empty_entries(tmp_path: Path):
    manifest_path = tmp_path / "entitlements.json"
    manifest_path.write_text(
        json.dumps({"namespaces": {"ui": {"entitlements": []}}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must be a non-empty array"):
        load_entitlements_manifest(tmp_path)


def test_load_entitlements_manifest_rejects_duplicate_keys(tmp_path: Path):
    manifest_path = tmp_path / "entitlements.json"
    manifest_path.write_text(
        json.dumps(
            {
                "namespaces": {
                    "ui": {
                        "entitlements": [
                            {"key": "ui:menu:operator", "resource": 'ui::Menu::"operator"'},
                            {"key": "ui:menu:operator", "resource": 'ui::Menu::"debug"'},
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate entitlement key"):
        load_entitlements_manifest(tmp_path)
