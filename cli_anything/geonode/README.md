# cli-anything-geonode

CLI harness for [GeoNode](https://geonode.org/) — a geospatial content management system. Wraps 100% of the GeoNode REST API v2 with 18 command groups and ~90 client methods.

## Prerequisites

A running GeoNode instance is required. GeoNode is a web application — this CLI talks to it via its REST API v2.

```bash
# Option 1: Docker Compose (recommended)
git clone https://github.com/GeoNode/geonode.git
cd geonode
docker compose up -d

# Option 2: Docker (quick test)
docker run -d -p 8000:8000 geonode/geonode:latest
```

## Installation

```bash
cd agent-harness
pip install -e .
```

Verify:
```bash
which cli-anything-geonode
cli-anything-geonode --version
```

## Configuration

```bash
# Set your GeoNode instance URL
cli-anything-geonode config set-url http://localhost:8000

# Set API token (get from GeoNode admin: /admin/authtoken/tokenproxy/)
cli-anything-geonode config set-token <your-api-key>

# Or use Basic Auth
cli-anything-geonode config set-credentials admin geonode

# Test connection
cli-anything-geonode config test

# View current config (secrets masked)
cli-anything-geonode config show

# Reset to defaults
cli-anything-geonode config clear
```

Environment variables are also supported:
```bash
export GEONODE_URL=http://localhost:8000
export GEONODE_TOKEN=<your-api-key>
# Or for Basic Auth:
export GEONODE_USER=admin
export GEONODE_PASSWORD=geonode
```

Config is saved to `~/.cli-anything-geonode/config.json`.

## Global Options

```
--url TEXT           GeoNode instance URL (overrides config)
--token TEXT         API key / OAuth token (overrides config)
--user TEXT          Username for Basic Auth
--password TEXT      Password for Basic Auth
--json               Output as JSON (for agent/script consumption)
--page-size INTEGER  Results per page (default: 10)
--version            Show version and exit
--help               Show help and exit
```

## Interactive REPL

Run without a subcommand to enter interactive mode with command completion and history:

```bash
cli-anything-geonode
```

---

## Command Reference

### `config` — Connection Configuration

```bash
cli-anything-geonode config show                       # Show current config
cli-anything-geonode config set-url <url>               # Set GeoNode URL
cli-anything-geonode config set-token <token>            # Set API token
cli-anything-geonode config set-credentials <user> <pw>  # Set Basic Auth
cli-anything-geonode config test                         # Test connection
cli-anything-geonode config clear                        # Reset to defaults
```

### `dataset` — Dataset (Layer) Management

```bash
# List with filters
cli-anything-geonode dataset list
cli-anything-geonode dataset list --owner admin --category environment
cli-anything-geonode dataset list --keyword rivers --search "water quality"
cli-anything-geonode dataset list --page 2

# Details
cli-anything-geonode dataset info 42

# Upload geospatial data (Shapefile, GeoTIFF, GeoJSON, GeoPackage, CSV, KML)
cli-anything-geonode dataset upload ./cities.geojson --title "World Cities" --abstract "Major cities"
cli-anything-geonode dataset upload ./dem.tif --title "Digital Elevation Model" --category elevation
cli-anything-geonode dataset upload ./roads.shp.zip --keyword roads --keyword transport

# Update metadata
cli-anything-geonode dataset update 42 --title "Updated Title" --abstract "New description"

# Delete
cli-anything-geonode dataset delete 42 --confirm

# Permissions
cli-anything-geonode dataset permissions 42
cli-anything-geonode dataset permissions 42 --set-json '{"users":{"admin":["view","download"]}}'

# Upload ISO metadata XML
cli-anything-geonode dataset metadata 42 ./metadata.xml

# Relationships
cli-anything-geonode dataset maps 42           # Maps using this dataset
cli-anything-geonode dataset maplayers 42      # Map layers referencing this dataset
```

### `map` — Map Management

```bash
# List and search
cli-anything-geonode map list
cli-anything-geonode map list --search "land use"

# Details
cli-anything-geonode map info 10

# Create
cli-anything-geonode map create --title "Land Use Map" --abstract "Urban planning map"

# Update
cli-anything-geonode map update 10 --title "Updated Map Title"

# Delete
cli-anything-geonode map delete 10 --confirm

# Relationships
cli-anything-geonode map layers 10       # Map layers in this map
cli-anything-geonode map datasets 10     # Datasets used in this map
```

### `document` — Document Management

```bash
# List and search
cli-anything-geonode document list
cli-anything-geonode document list --search "annual report"

# Details
cli-anything-geonode document info 5

# Upload any file type
cli-anything-geonode document upload ./report.pdf --title "Annual Report 2024"
cli-anything-geonode document upload ./photo.jpg --title "Site Photo"

# Update metadata
cli-anything-geonode document update 5 --title "Updated Title"

# Delete
cli-anything-geonode document delete 5 --confirm

# Relationships
cli-anything-geonode document linked-resources 5
```

### `geoapp` — GeoApp Management

```bash
cli-anything-geonode geoapp list
cli-anything-geonode geoapp list --search "dashboard"
cli-anything-geonode geoapp info 3
cli-anything-geonode geoapp create --title "My Dashboard"
cli-anything-geonode geoapp update 3 --title "Updated Dashboard"
cli-anything-geonode geoapp delete 3 --confirm
```

### `resource` — Unified Resource Operations

Works across all resource types (datasets, maps, documents, geoapps).

```bash
# List and search
cli-anything-geonode resource list
cli-anything-geonode resource list --type dataset           # Filter by type
cli-anything-geonode resource list --search "environment"
cli-anything-geonode resource search "river basin"

# Details
cli-anything-geonode resource info 42

# Copy (async — returns execution_id)
cli-anything-geonode resource copy 42

# Delete
cli-anything-geonode resource delete 42 --confirm

# Filtered lists
cli-anything-geonode resource approved                # Approved resources
cli-anything-geonode resource published               # Published resources
cli-anything-geonode resource featured                # Featured resources
cli-anything-geonode resource favorites               # Your favorites

# Resource types with counts
cli-anything-geonode resource types

# Favorites
cli-anything-geonode resource favorite 42             # Add to favorites
cli-anything-geonode resource favorite 42 --remove    # Remove from favorites

# Permissions
cli-anything-geonode resource permissions 42
cli-anything-geonode resource permissions 42 --set-json '{"users":{"admin":["view"]}}'

# Thumbnails
cli-anything-geonode resource set-thumbnail 42 --file ./thumb.png
cli-anything-geonode resource set-thumbnail 42 --url "http://example.com/thumb.png"

# Extra metadata
cli-anything-geonode resource extra-metadata 42
cli-anything-geonode resource extra-metadata 42 --set-json '{"custom_field":"value"}'
cli-anything-geonode resource extra-metadata 42 --delete

# ISO metadata XML
cli-anything-geonode resource iso-metadata 42

# Linked resources
cli-anything-geonode resource linked-resources 42
cli-anything-geonode resource linked-resources 42 --add "10,11,12"
cli-anything-geonode resource linked-resources 42 --remove "10"

# Assets
cli-anything-geonode resource upload-asset 42 ./supplementary_data.csv
cli-anything-geonode resource delete-asset 42 99
```

### `user` — User Management

```bash
# List
cli-anything-geonode user list
cli-anything-geonode user list --page 2

# Details
cli-anything-geonode user info 1

# Current authenticated user
cli-anything-geonode user me

# Create (admin only)
cli-anything-geonode user create newuser password123 --email user@example.com --first-name John --last-name Doe

# Update
cli-anything-geonode user update 5 --first-name Jane --email jane@example.com

# Delete (admin only)
cli-anything-geonode user delete 5 --confirm
```

### `group` — Group Management

```bash
cli-anything-geonode group list
cli-anything-geonode group info 1
cli-anything-geonode group members 1      # List members
cli-anything-geonode group managers 1     # List managers
cli-anything-geonode group resources 1    # Resources owned by group
```

### `upload` — Upload Monitoring

```bash
# List recent uploads
cli-anything-geonode upload list

# Check upload status
cli-anything-geonode upload status 42

# View limits
cli-anything-geonode upload size-limits
cli-anything-geonode upload parallelism-limits

# List imports (new importer)
cli-anything-geonode upload imports
```

### `execution` — Async Execution Requests

GeoNode runs many operations asynchronously (copy, create, delete). Track them here.

```bash
# List your execution requests
cli-anything-geonode execution list

# Check specific request
cli-anything-geonode execution info abc-123-def

# Check operation status
cli-anything-geonode execution status abc-123-def

# Delete completed request
cli-anything-geonode execution delete abc-123-def
```

### `harvester` — Remote Service Harvesting

Import datasets from remote OGC services (WMS, WFS, CSW).

```bash
# List harvesters
cli-anything-geonode harvester list

# Details
cli-anything-geonode harvester info 1

# Create harvester for a remote WMS
cli-anything-geonode harvester create --name "Remote WMS" --url "http://wms.example.com/wms" --type wms

# Update
cli-anything-geonode harvester update 1 --name "Updated Name"

# View harvestable resources
cli-anything-geonode harvester harvestable-resources 1

# View harvesting sessions
cli-anything-geonode harvester sessions
cli-anything-geonode harvester session-info 5
```

### `metadata` — Metadata Management

ISO-compliant metadata management with schema validation and autocomplete.

```bash
# Metadata endpoint info
cli-anything-geonode metadata info

# Get JSON schema for metadata
cli-anything-geonode metadata schema
cli-anything-geonode metadata schema --pk 42      # Schema for specific resource

# Get/update metadata instance
cli-anything-geonode metadata instance 42
cli-anything-geonode metadata instance 42 --set-json '{"title":"New Title","abstract":"Updated"}'

# Autocomplete (for building metadata forms)
cli-anything-geonode metadata autocomplete users --query "adm"
cli-anything-geonode metadata autocomplete categories --query "env"
cli-anything-geonode metadata autocomplete regions --query "asia"
cli-anything-geonode metadata autocomplete hkeywords --query "water"
cli-anything-geonode metadata autocomplete groups --query "editor"
cli-anything-geonode metadata autocomplete licenses --query "creative"
```

### `facet` — Faceted Search

Faceted search for resource discovery.

```bash
# List available facets
cli-anything-geonode facet list

# Get facet topics with counts
cli-anything-geonode facet get category
cli-anything-geonode facet get keyword --contains "water" --lang en
cli-anything-geonode facet get owner --page 2
```

### `category` — Topic Categories

ISO 19115 topic categories.

```bash
cli-anything-geonode category list
cli-anything-geonode category info 1
```

### `region` — Geographic Regions

Hierarchical geographic regions.

```bash
cli-anything-geonode region list
cli-anything-geonode region list --page 2
cli-anything-geonode region info 1
```

### `keyword` — Keywords & Thesaurus

Hierarchical keywords and thesaurus keyword management.

```bash
# Hierarchical keywords
cli-anything-geonode keyword list
cli-anything-geonode keyword info 1

# Thesaurus keywords
cli-anything-geonode keyword thesaurus
cli-anything-geonode keyword thesaurus-info 1
```

### `owner` — Resource Owners

```bash
cli-anything-geonode owner list
cli-anything-geonode owner info 1
```

### `schema` — OpenAPI Schema

```bash
cli-anything-geonode schema     # Get full OpenAPI 3.0 schema
```

---

## JSON Mode

Every command supports `--json` for machine-readable output:

```bash
# Pipe to jq for processing
cli-anything-geonode --json dataset list | jq '.datasets[].title'

# Use in scripts
DATASET_ID=$(cli-anything-geonode --json dataset list | jq '.datasets[0].pk')

# Agent-friendly: structured error output
cli-anything-geonode --json dataset info 999999
# {"error": "GeoNode API error: 404 Not Found", "status_code": 404}
```

## Python API (Programmatic Use)

```python
from cli_anything.geonode.core.client import GeoNodeClient

client = GeoNodeClient(url="http://localhost:8000", token="your-api-key")

# List datasets
datasets = client.list_datasets(page_size=50, search="rivers")
print(f"Found {datasets['total']} datasets")

# Upload a dataset
result = client.upload_dataset("./cities.geojson", title="World Cities")
upload_id = result["id"]

# Poll until complete
status = client.poll_upload(upload_id, timeout=120)
print(f"Upload {status['state']}")

# Search across all resources
results = client.search_resources("environment", page_size=20)

# Manage favorites
client.add_favorite(42)
favorites = client.list_favorite_resources()

# Get ISO metadata
xml = client.get_iso_metadata_xml(42)

# Autocomplete for building UIs
users = client.autocomplete_users("adm")
categories = client.autocomplete_categories("env")
```

## Supported Upload Formats

| Format | Extension | Type |
|--------|-----------|------|
| Shapefile | .shp.zip | Vector |
| GeoTIFF | .tif, .tiff | Raster |
| GeoJSON | .geojson, .json | Vector |
| GeoPackage | .gpkg | Vector |
| CSV | .csv | Tabular |
| KML | .kml | Vector |
| Cloud Optimized GeoTIFF | .tif (COG) | Raster |
| SLD Style | .sld | Style |

## Running Tests

```bash
# Unit tests — 142 tests, no GeoNode required
python3 -m pytest cli_anything/geonode/tests/test_core.py -v

# E2E tests — requires running GeoNode
export GEONODE_URL=http://localhost:8000
export GEONODE_TOKEN=<your-token>
python3 -m pytest cli_anything/geonode/tests/test_full_e2e.py -v -s

# All tests with installed CLI
CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/geonode/tests/ -v -s
```

## API Endpoint Coverage

| Endpoint Group | Methods | CLI Commands |
|----------------|---------|--------------|
| Datasets | list, get, update, replace, delete, metadata, permissions, maplayers, maps | 9 |
| Maps | list, get, create, update, replace, delete, layers, datasets | 8 |
| Documents | list, get, upload, update, replace, delete, linked-resources | 7 |
| GeoApps | list, get, create, update, replace, delete | 6 |
| Resources | list, search, get, create, update, replace, delete, copy, permissions (GET/PUT/PATCH/DELETE), approved, published, featured, favorites, favorite (add/remove), types, set-thumbnail, set-thumbnail-from-bbox, extra-metadata (GET/PUT/POST/DELETE), iso-metadata, linked-resources (GET/POST/DELETE), assets (POST/DELETE), async-create, async-update, async-delete | 18 |
| Users | list, get, create, update, delete, user-info, roles, admin-role | 8 |
| Groups | list, get, members, managers, resources | 5 |
| Uploads | list, get, poll, upload-dataset, imports, size-limits, parallelism-limits | 7 |
| Execution | list, get, status, delete | 4 |
| Harvesters | list, get, create, update, harvestable-resources, sessions, session-detail | 7 |
| Metadata | info, schema, instance (GET/PATCH/PUT), autocomplete (7 entities) | 10 |
| Facets | list, get | 2 |
| Categories | list, get | 2 |
| Regions | list, get | 2 |
| Keywords | list, get, thesaurus-list, thesaurus-get | 4 |
| Owners | list, get | 2 |
| Schema | openapi | 1 |
| Auth | verify-token, get-roles, get-admin-role | 3 |
| **Total** | **~90 methods** | **~105 operations** |
