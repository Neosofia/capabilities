"""Discover UI capability checks from Cedar policy permits (convention, no manifest)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ACTION = "View"
UI_RESOURCE = re.compile(r'resource\s*==\s*(ui::\w+::"(?:[^"\\]|\\.)*")')
VIEW_ACTION = re.compile(r'action\s*==\s*Action::"View"')


@dataclass(frozen=True)
class EntitlementDefinition:
    """One UI capability: Cedar entity id is both the API key and authorization resource."""

    entity_id: str
    action: str

    @property
    def key(self) -> str:
        return self.entity_id

    @property
    def resource(self) -> str:
        return self.entity_id


@dataclass(frozen=True)
class EntitlementsManifest:
    namespaces: dict[str, list[EntitlementDefinition]]

    @property
    def namespace_names(self) -> list[str]:
        return sorted(self.namespaces.keys())


def _namespace_for_entity(entity_id: str) -> str:
    segment = entity_id.split("::", 1)[0].strip()
    if not segment:
        raise ValueError(f"UI entity id must start with a Cedar namespace: {entity_id!r}")
    return segment


def _discover_view_entitlements(text: str) -> list[str]:
    entity_ids: list[str] = []
    for match in UI_RESOURCE.finditer(text):
        permit_start = text.rfind("permit", 0, match.start())
        if permit_start == -1:
            continue
        block = text[permit_start : match.end() + 50]
        if not VIEW_ACTION.search(block):
            continue
        entity_ids.append(match.group(1))
    return entity_ids


def load_entitlements_catalog(policies_dir: Path) -> EntitlementsManifest:
    cedar_files = sorted(policies_dir.rglob("*.cedar"))
    if not cedar_files:
        raise FileNotFoundError(
            f"No Cedar policy files found under {policies_dir}. "
            "Product policy bundles must include ui/*.cedar policies.",
        )

    namespaces: dict[str, list[EntitlementDefinition]] = {}
    seen: dict[str, Path] = {}

    for path in cedar_files:
        for entity_id in _discover_view_entitlements(path.read_text(encoding="utf-8")):
            if entity_id in seen:
                raise ValueError(
                    f"Duplicate UI entity {entity_id!r} in {path} "
                    f"(already declared in {seen[entity_id]})",
                )
            seen[entity_id] = path
            namespace = _namespace_for_entity(entity_id)
            namespaces.setdefault(namespace, []).append(
                EntitlementDefinition(entity_id=entity_id, action=DEFAULT_ACTION),
            )

    if not namespaces:
        raise ValueError(
            f"No View permits on ui:: entities found under {policies_dir}. "
            "See CDP policies/capabilities/CONVENTIONS.md.",
        )

    for definitions in namespaces.values():
        definitions.sort(key=lambda item: item.entity_id)

    return EntitlementsManifest(namespaces=namespaces)
