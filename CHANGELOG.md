# Changelog

Changes for consumers of the Capabilities service. Deploy steps: [OPERATIONS.md](OPERATIONS.md).

## [0.7.4] - 2026-06-18

### Fixed

- Service errors and API failures are recorded in operational logs at default verbosity.

## [0.7.3] - 2026-06-16

### Changed

- Bump dev dependency pins for Trivy (`cryptography>=48.0.1`, `pyjwt>=2.13.0`).

## [0.7.2] - 2026-06-16

### Changed

- UI entitlement keys are Cedar entity ids (`ui::Menu::"clinician"`, etc.) discovered from `View` permits on `ui::` resources; `entitlements.json` and annotation comments are not used.
- Pinned **`POLICIES_IMAGE=ghcr.io/neosofia/cdp-policies:v0.3.0`**.

## [0.7.1] - 2026-06-15

### Changed

- Pinned the production policy bundle build arg to **`POLICIES_IMAGE=ghcr.io/neosofia/cdp-policies:v0.2.0`** so Capabilities ships the same CDP entitlement bundle as User.

## [0.7.0] - 2026-06-14

### Changed

- Pinned **`authorization-in-the-middle/v0.7.1`** (no API changes in this service).

## [0.6.0] - 2026-06-10

### Changed

- Pinned **`authorization-in-the-middle/v0.4.23`** (hyphenated catalog type inference fix for downstream services; no API changes in this service).
