# cli-anything-geonode

CLI harness for [GeoNode](https://geonode.org/) — a geospatial content management system.

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
```

Environment variables are also supported:
```bash
export GEONODE_URL=http://localhost:8000
export GEONODE_TOKEN=<your-api-key>
```

## Usage

### One-shot commands

```bash
# List datasets
cli-anything-geonode dataset list
cli-anything-geonode --json dataset list

# Dataset details
cli-anything-geonode dataset info 42

# Upload a dataset
cli-anything-geonode dataset upload ./cities.geojson --title "World Cities"

# Search resources
cli-anything-geonode resource search "rivers"

# List maps
cli-anything-geonode map list

# Create a map
cli-anything-geonode map create --title "My Map"

# Upload a document
cli-anything-geonode document upload ./report.pdf --title "Annual Report"

# List users
cli-anything-geonode user list

# List groups
cli-anything-geonode group list
cli-anything-geonode group members 1
```

### JSON mode (for agents)

```bash
cli-anything-geonode --json dataset list
cli-anything-geonode --json resource search "test"
```

### Interactive REPL

```bash
cli-anything-geonode
# Enters interactive mode with command completion and history
```

## Command Groups

| Group | Description |
|-------|-------------|
| `config` | Connection configuration (URL, token, credentials) |
| `dataset` | Dataset/layer CRUD, upload, permissions |
| `map` | Map CRUD, layer management |
| `document` | Document CRUD, upload |
| `resource` | Unified resource list, search, permissions, copy |
| `user` | User listing and details |
| `group` | Group listing, members, resources |
| `upload` | Upload monitoring and status |

## Running Tests

```bash
# Unit tests (no GeoNode required)
pytest cli_anything/geonode/tests/test_core.py -v

# E2E tests (requires running GeoNode)
export GEONODE_URL=http://localhost:8000
export GEONODE_TOKEN=<your-token>
pytest cli_anything/geonode/tests/test_full_e2e.py -v -s

# All tests with installed CLI
CLI_ANYTHING_FORCE_INSTALLED=1 pytest cli_anything/geonode/tests/ -v -s
```

## Supported Upload Formats

- Shapefile (.shp.zip)
- GeoTIFF (.tif, .tiff)
- GeoJSON (.geojson, .json)
- GeoPackage (.gpkg)
- CSV (.csv)
- KML (.kml)
- Cloud Optimized GeoTIFF (COG)
