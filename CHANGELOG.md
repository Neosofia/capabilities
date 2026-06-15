# Changelog

Changes for consumers of the Capabilities service. Deploy steps: [OPERATIONS.md](OPERATIONS.md).

## [0.7.1] - 2026-06-15

### Changed

- Pinned the production policy bundle build arg to **`POLICIES_IMAGE=ghcr.io/neosofia/cdp-policies:v0.2.0`** so Capabilities ships the same CDP entitlement bundle as User.

## [0.7.0] - 2026-06-14

### Changed

- Pinned **`authorization-in-the-middle/v0.7.1`** (no API changes in this service).

## [0.6.0] - 2026-06-10

### Changed

- Pinned **`authorization-in-the-middle/v0.4.23`** (hyphenated catalog type inference fix for downstream services; no API changes in this service).
