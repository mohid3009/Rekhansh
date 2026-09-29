---
tags: [file, config, seed]
---
# config.py
`backend/app/config.py`

## Overview
Centralized configuration management module providing typed Pydantic models, directory paths, and YAML parser bindings for all backend subsystems.

## Key Responsibilities
- **Path Resolution Constants**:
  - Resolves absolute filesystem paths for `DATA_DIR` (`backend/data`), `CONFIG_DIR` (`backend/config`), and generated raster artifact stores.
- **Typed Settings Parsing**:
  - `load_site_config()`: Parses `site.yaml` into strongly typed `SiteConfig` objects with coordinate and zoom validations.
  - `load_triage_config()`: Parses `triage.yaml` into `TriageConfig` objects with mathematical threshold constraints.
- **Environment Overrides**:
  - Ingests environment variable overrides for database URIs, API keys, CORS origins, and runtime deployment modes.
- **Fail-Fast Configuration Validation**:
  - Ensures required data directories and core configuration files exist at application startup to prevent runtime execution failures.
