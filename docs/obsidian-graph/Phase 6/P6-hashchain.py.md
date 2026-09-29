---
tags: [file, pipeline, crypto, hashchain]
---
# hashchain.py
`backend/app/pipeline/hashchain.py`

## Overview
US-5.3 — Cryptographic tamper-evident audit ledger engine. Enforces data integrity across parcel version chains using chained SHA-256 cryptographic hashes.

## Key Responsibilities
- **Cryptographic Hash Generation (`compute_hash`)**:
  - Serializes version payloads into deterministic canonical JSON (sorted keys, compact separators).
  - Computes SHA-256 digest over the combined string:
    $$\text{Hash}_n = \text{SHA256}(\text{Hash}_{n-1} \,\|\, \text{Timestamp} \,\|\, \text{Author} \,\|\, \text{Geometry} \,\|\, \text{Action})$$
- **Genesis Block Anchoring**:
  - Seeds initial Version 0 records with a fixed genesis parent hash (`0000000000000000000000000000000000000000000000000000000000000000`).
- **Chain Verification (`verify_chain`)**:
  - Validates full historical integrity by recalculating digests from Genesis to the latest version.
  - Detects unauthorized database modifications, record deletions, or retroactive boundary tampering.
