import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ACTION = "View"
MANIFEST_FILENAME = "entitlements.json"


@dataclass(frozen=True)
class EntitlementDefinition:
    key: str
    resource: str
    action: str


@dataclass(frozen=True)
class EntitlementsManifest:
    namespaces: dict[str, list[EntitlementDefinition]]

    @property
    def namespace_names(self) -> list[str]:
        return sorted(self.namespaces.keys())


def _parse_entitlement_entries(
    entries: object,
    *,
    manifest_path: Path,
    namespace: str,
) -> list[EntitlementDefinition]:
    if not isinstance(entries, list) or not entries:
        raise ValueError(
            f"{manifest_path} namespaces.{namespace}.entitlements must be a non-empty array"
        )

    definitions: list[EntitlementDefinition] = []
    seen_keys: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"namespaces.{namespace}.entitlements[{index}] must be an object")

        key = entry.get("key")
        resource = entry.get("resource")
        if not isinstance(key, str) or not key.strip():
            raise ValueError(
                f"namespaces.{namespace}.entitlements[{index}] requires a non-empty 'key'"
            )
        if not isinstance(resource, str) or not resource.strip():
            raise ValueError(
                f"namespaces.{namespace}.entitlements[{index}] requires a non-empty 'resource'"
            )
        if key in seen_keys:
            raise ValueError(f"Duplicate entitlement key in namespace '{namespace}': {key}")

        action = entry.get("action", DEFAULT_ACTION)
        if not isinstance(action, str) or not action.strip():
            raise ValueError(
                f"namespaces.{namespace}.entitlements[{index}] 'action' must be a non-empty string"
            )

        seen_keys.add(key)
        definitions.append(EntitlementDefinition(key=key, resource=resource, action=action))

    return definitions


def load_entitlements_manifest(policies_dir: Path) -> EntitlementsManifest:
    manifest_path = policies_dir / MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"Entitlements manifest not found at {manifest_path}. "
            "Product policy bundles must include entitlements.json."
        )

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    namespaces_raw = data.get("namespaces")
    if not isinstance(namespaces_raw, dict) or not namespaces_raw:
        raise ValueError(f"{manifest_path} must define a non-empty 'namespaces' object")

    namespaces: dict[str, list[EntitlementDefinition]] = {}
    for namespace, namespace_config in namespaces_raw.items():
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError(f"{manifest_path} namespace keys must be non-empty strings")
        if not isinstance(namespace_config, dict):
            raise ValueError(f"namespaces.{namespace} must be an object")

        entries = namespace_config.get("entitlements")
        namespaces[namespace] = _parse_entitlement_entries(
            entries,
            manifest_path=manifest_path,
            namespace=namespace,
        )

    return EntitlementsManifest(namespaces=namespaces)
