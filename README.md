# GeoNode CLI Harness — SOP

## What is GeoNode?

GeoNode is an open-source geospatial content management system (CMS) built on Django, GeoDjango, GeoServer, and PostGIS. It enables organizations to share, discover, and manage geospatial data through a web interface.

> **For end users:** If you use GeoNode from a web browser (uploading datasets, creating maps, managing permissions), see [USER_GUIDE.md](USER_GUIDE.md).

## Architecture

- **Framework:** Django + GeoDjango + Django REST Framework (dynamic-rest)
- **Database:** PostgreSQL + PostGIS
- **Geospatial services:** GeoServer (WMS/WFS/WCS), pyCSW (catalog)
- **Auth:** OAuth2, API key, session-based, Basic Auth
- **Async tasks:** Celery + RabbitMQ/Redis
- **REST API:** `/api/v2/` — 150+ endpoints across 18 resource domains

## How This CLI Works

Unlike typical cli-anything tools that manipulate local project files and invoke local binaries, GeoNode is a **web application**. This CLI acts as a **REST API client**:

1. Connects to a running GeoNode instance over HTTP
2. Wraps 100% of `/api/v2/` endpoints with Click commands
3. Handles authentication (Bearer token or Basic Auth)
4. Supports JSON output mode for AI agent consumption
5. Provides interactive REPL for human users

## Backend Dependency

**GeoNode must be running and accessible.** This is not a local binary dependency — it's a network service dependency. The CLI is useless without a GeoNode instance.

```bash
docker compose up -d
```

## Complete API Endpoint Coverage

### Datasets (Layers)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/datasets/` | List datasets with filters (owner, category, keyword, search, pagination) |
| GET | `/api/v2/datasets/{id}/` | Dataset details |
| PATCH | `/api/v2/datasets/{id}/` | Partial metadata update |
| PUT | `/api/v2/datasets/{id}/` | Full metadata update |
| DELETE | `/api/v2/datasets/{id}/` | Delete dataset |
| PUT | `/api/v2/datasets/{id}/metadata/` | Upload ISO metadata XML |
| GET | `/api/v2/datasets/{id}/permissions/` | Get permissions |
| PUT | `/api/v2/datasets/{id}/permissions/` | Set permissions |
| GET | `/api/v2/datasets/{id}/maplayers/` | Map layers referencing dataset |
| GET | `/api/v2/datasets/{id}/maps/` | Maps using dataset |

### Maps
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/maps/` | List maps |
| POST | `/api/v2/maps/` | Create map |
| GET | `/api/v2/maps/{id}/` | Map details |
| PATCH | `/api/v2/maps/{id}/` | Partial update |
| PUT | `/api/v2/maps/{id}/` | Full update |
| DELETE | `/api/v2/maps/{id}/` | Delete map |
| GET | `/api/v2/maps/{id}/maplayers/` | Layers in map |
| GET | `/api/v2/maps/{id}/datasets/` | Datasets in map |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/documents/` | List documents |
| POST | `/api/v2/documents/` | Upload document |
| GET | `/api/v2/documents/{id}/` | Document details |
| PATCH | `/api/v2/documents/{id}/` | Partial update |
| PUT | `/api/v2/documents/{id}/` | Full update |
| DELETE | `/api/v2/documents/{id}/` | Delete document |
| GET | `/api/v2/documents/{id}/linked-resources/` | Linked resources |

### GeoApps
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/geoapps/` | List geoapps |
| POST | `/api/v2/geoapps/` | Create geoapp |
| GET | `/api/v2/geoapps/{id}/` | Details |
| PATCH | `/api/v2/geoapps/{id}/` | Partial update |
| PUT | `/api/v2/geoapps/{id}/` | Full update |
| DELETE | `/api/v2/geoapps/{id}/` | Delete |

### Resources (Unified — ResourceBase)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/resources/` | List all resources |
| POST | `/api/v2/resources/` | Create resource |
| GET | `/api/v2/resources/{id}/` | Resource details |
| PATCH | `/api/v2/resources/{id}/` | Partial update |
| PUT | `/api/v2/resources/{id}/` | Full update |
| DELETE | `/api/v2/resources/{id}/` | Delete |
| PUT | `/api/v2/resources/{id}/copy/` | Clone resource (async) |
| GET | `/api/v2/resources/approved/` | Approved resources |
| GET | `/api/v2/resources/published/` | Published resources |
| GET | `/api/v2/resources/featured/` | Featured resources |
| GET | `/api/v2/resources/favorites/` | User's favorites |
| POST | `/api/v2/resources/{id}/favorite/` | Add to favorites |
| DELETE | `/api/v2/resources/{id}/favorite/` | Remove from favorites |
| GET | `/api/v2/resources/resource-types/` | Types with counts |
| GET | `/api/v2/resources/{id}/permissions/` | Get permissions |
| PUT | `/api/v2/resources/{id}/permissions/` | Set permissions |
| PATCH | `/api/v2/resources/{id}/permissions/` | Patch permissions |
| DELETE | `/api/v2/resources/{id}/permissions/` | Clear permissions |
| PUT | `/api/v2/resources/{id}/set-thumbnail/` | Set thumbnail (file/URL/base64) |
| POST | `/api/v2/resources/{id}/set-thumbnail-from-bbox/` | Thumbnail from bbox |
| GET | `/api/v2/resources/{id}/extra-metadata/` | Get extra metadata |
| PUT | `/api/v2/resources/{id}/extra-metadata/` | Update extra metadata |
| POST | `/api/v2/resources/{id}/extra-metadata/` | Add extra metadata |
| DELETE | `/api/v2/resources/{id}/extra-metadata/` | Delete extra metadata |
| GET | `/api/v2/resources/{id}/iso-metadata-xml/` | ISO metadata XML |
| GET | `/api/v2/resources/{id}/linked-resources/` | Get linked resources |
| POST | `/api/v2/resources/{id}/linked-resources/` | Add linked resources |
| DELETE | `/api/v2/resources/{id}/linked-resources/` | Remove linked resources |
| POST | `/api/v2/resources/{id}/assets/` | Upload asset |
| DELETE | `/api/v2/resources/{id}/assets/{asset_id}/` | Delete asset |
| POST | `/api/v2/resources/create/{type}/` | Async create |
| PUT | `/api/v2/resources/{id}/update/` | Async update |
| DELETE | `/api/v2/resources/{id}/delete/` | Async delete |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/users/` | List users |
| POST | `/api/v2/users/` | Create user |
| GET | `/api/v2/users/{id}/` | User details |
| PATCH | `/api/v2/users/{id}/` | Update user |
| DELETE | `/api/v2/users/{id}/` | Delete user |
| GET | `/api/v2/user-info/` | Authenticated user info |
| GET | `/api/v2/roles/` | Available roles |
| GET | `/api/v2/admin-role/` | Admin role info |
| POST | `/api/v2/verify-token/` | Verify access token |

### Groups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/groups/` | List groups |
| GET | `/api/v2/groups/{id}/` | Group details |
| GET | `/api/v2/groups/{id}/members/` | Members |
| GET | `/api/v2/groups/{id}/managers/` | Managers |
| GET | `/api/v2/groups/{id}/resources/` | Group resources |

### Uploads / Imports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/uploads/upload/` | Upload dataset (async) |
| GET | `/api/v2/uploads/` | List uploads |
| GET | `/api/v2/uploads/{id}/` | Upload status |
| GET | `/api/v2/imports/` | List imports (new importer) |
| POST | `/api/v2/imports/` | Create import |
| GET | `/api/v2/upload-size-limits/` | Size limits |
| POST | `/api/v2/upload-size-limits/` | Create size limit |
| GET | `/api/v2/upload-parallelism-limits/` | Parallelism limits |
| POST | `/api/v2/upload-parallelism-limits/` | Create parallelism limit |

### Execution Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/executionrequest/` | List execution requests |
| GET | `/api/v2/executionrequest/{id}/` | Request details |
| DELETE | `/api/v2/executionrequest/{id}/` | Delete request |
| GET | `/api/v2/resource-service/execution-status/{id}/` | Operation status |

### Harvesters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/harvesters/` | List harvesters |
| POST | `/api/v2/harvesters/` | Create harvester |
| GET | `/api/v2/harvesters/{id}/` | Details |
| PATCH | `/api/v2/harvesters/{id}/` | Update |
| GET | `/api/v2/harvesters/{id}/harvestable-resources/` | Harvestable resources |
| PATCH | `/api/v2/harvesters/{id}/harvestable-resources/` | Select resources |
| GET | `/api/v2/harvesting-sessions/` | Sessions |
| GET | `/api/v2/harvesting-sessions/{id}/` | Session details |

### Metadata
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/metadata/` | Info |
| GET | `/api/v2/metadata/schema/` | JSON schema |
| GET | `/api/v2/metadata/schema/{pk}/` | Schema for resource |
| GET | `/api/v2/metadata/instance/{pk}/` | Metadata instance |
| PUT | `/api/v2/metadata/instance/{pk}/` | Full update |
| PATCH | `/api/v2/metadata/instance/{pk}/` | Partial update |
| GET | `/api/v2/metadata/autocomplete/{entity}/` | Autocomplete (users, resources, regions, hkeywords, groups, categories, licenses) |
| GET | `/api/v2/metadata/autocomplete/thesaurus/{id}/keywords/` | Thesaurus autocomplete |

### Facets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/facets/` | List facets |
| GET | `/api/v2/facets/{name}/` | Facet topics |

### Catalog (Categories, Regions, Keywords, Owners)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/categories/` | Topic categories |
| GET | `/api/v2/categories/{id}/` | Category details |
| GET | `/api/v2/regions/` | Geographic regions |
| GET | `/api/v2/regions/{id}/` | Region details |
| GET | `/api/v2/keywords/` | Hierarchical keywords |
| GET | `/api/v2/keywords/{id}/` | Keyword details |
| GET | `/api/v2/tkeywords/` | Thesaurus keywords |
| GET | `/api/v2/tkeywords/{id}/` | Thesaurus keyword details |
| GET | `/api/v2/owners/` | Resource owners |
| GET | `/api/v2/owners/{id}/` | Owner details |

### Schema
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/schema/` | OpenAPI 3.0 schema |

## API Parameter Reference

All create/update/replace methods accept explicit keyword parameters derived from the GeoNode OpenAPI schema. Parameters default to `None` (omitted from the request). Additional unlisted fields can be passed via `**kwargs`.

### Common ResourceBase Fields

These fields are shared by **all resource types** (Dataset, Map, Document, GeoApp, Resource):

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `title` | str | Resource title | `"My Dataset"` |
| `abstract` | str | Resource description | `"Temperature data for 2024"` |
| `category` | str | Topic category identifier (nullable) | `"environment"`, `"climatologyMeteorologyAtmosphere"`, `"society"` |
| `group` | str | Group name or identifier (nullable) | `"my-project-group"` |
| `keywords` | str | Comma-separated keywords (nullable) | `"climate,water,temperature"` |
| `tkeywords` | str | Thesaurus keywords (nullable) | |
| `regions` | str | Region codes (nullable) | `"ITA"`, `"EUR"` |
| `license` | str | License identifier (nullable) | `"cc-by-4.0"`, `"public_domain"`, `"not_specified"` |
| `restriction_code_type` | str | Access restriction (nullable) | `"otherRestrictions"`, `"copyright"` |
| `date` | datetime | Resource date | `"2024-01-15T00:00:00Z"` |
| `date_type` | str | Date type | `"creation"`, `"publication"`, `"revision"` |
| `temporal_extent_start` | datetime | Temporal coverage start | `"2020-01-01T00:00:00Z"` |
| `temporal_extent_end` | datetime | Temporal coverage end | `"2024-12-31T00:00:00Z"` |
| `purpose` | str | Purpose of the resource | |
| `edition` | str | Edition or version | |
| `maintenance_frequency` | str | Update frequency | `"asNeeded"`, `"daily"`, `"annually"` |
| `supplemental_information` | str | Additional info | |
| `data_quality_statement` | str | Data quality statement | |
| `constraints_other` | str | Other constraints | |
| `srid` | str | Native spatial reference | `"EPSG:32632"`, `"EPSG:4326"` |
| `spatial_representation_type` | str | Spatial representation (nullable) | `"vector"`, `"grid"` |
| `extent` | dict | Geographic extent | `{"coords": [10.4, 46.2, 12.9, 47.2], "srid": "EPSG:4326"}` |
| `is_published` | bool | Published status | |
| `is_approved` | bool | Approved status | |
| `featured` | bool | Featured resource | |
| `advertised` | bool | Advertised in catalog | |
| `metadata_only` | bool | Metadata-only resource | |
| `metadata_uploaded_preserve` | bool | Preserve uploaded metadata | |
| `attribution` | str | Attribution text | |
| `doi` | str | Digital Object Identifier | `"10.1234/test"` |
| `language` | str | Language code | `"eng"`, `"ita"` |
| `embed_url` | str | Embed URL | |
| `resource_type` | str | Resource type identifier | `"dataset"`, `"map"`, `"document"` |
| `subtype` | str | Resource subtype (max 128 chars, nullable) | `"vector"`, `"raster"` |
| `blob` | any | Binary data (write-only) | |
| `popular_count` | str | View count | |
| `share_count` | str | Share count | |
| `rating` | str | Rating | |
| `poc` | list | Point of contact — list of user PKs | `[1060]` |
| `metadata_author` | list | Metadata author — list of user PKs | `[1060, 1001]` |
| `processor` | list | Processor contact — list of user PKs | `[]` |
| `publisher` | list | Publisher contact — list of user PKs | `[]` |
| `custodian` | list | Custodian — list of user PKs | `[]` |
| `distributor` | list | Distributor — list of user PKs | `[]` |
| `resource_user` | list | Resource user — list of user PKs | `[]` |
| `resource_provider` | list | Resource provider — list of user PKs | `[]` |
| `originator` | list | Originator — list of user PKs | `[]` |
| `principal_investigator` | list | Principal investigator — list of user PKs | `[]` |

### Map-Specific Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `maplayers` | list | List of layer dicts (see maplayer structure below) |
| `urlsuffix` | str | Site URL suffix (max 255 chars) |
| `featuredurl` | str | Featured map URL (max 255 chars) |

#### Maplayer Structure

Each item in `maplayers` is a dict with:

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Dataset alternate name, e.g. `"geonode:my_layer"` |
| `order` | int | Display stacking order (0 = bottom) |
| `visibility` | bool | Whether layer is visible on load |
| `opacity` | float | Layer opacity (0.0–1.0) |
| `current_style` | str | Active SLD style name |
| `extra_params` | dict | MapStore config: `{"msId": "uuid", "styles": []}` |

The `name` field references a dataset by its `alternate` identifier (available from `get_dataset()` or `list_datasets()`).

### Dataset-Specific Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `ptype` | str | Processing type (max 255 chars) |
| `ows_url` | uri | OWS service URL for this layer (max 200 chars, nullable) |
| `has_elevation` | bool | Whether dataset has elevation data |
| `has_time` | bool | Whether dataset has time dimension |
| `is_mosaic` | bool | Whether dataset is a mosaic |
| `elevation_regex` | str | Elevation regex pattern (max 128 chars, nullable) |
| `time_regex` | str | Time regex pattern (nullable) |
| `featureinfo_custom_template` | str | Custom GetFeatureInfo template |
| `data` | str | Data field |
| `metadata` | str | Metadata field (nullable) |

### Document-Specific Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `extension` | str | File extension (max 128 chars, nullable) |
| `doc_url` | uri | External document URL (max 512 chars, nullable) |

### GeoApp-Specific Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | GeoApp name (writable, unlike other resource types) |

### Harvester Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Harvester name (max 255 chars, required) |
| `remote_url` | uri | Base URL of remote service to harvest (required), e.g. `"https://example.com/geoserver/wms"` |
| `scheduling_enabled` | bool | Periodically schedule harvesting |
| `harvester_type` | enum | Harvester class — see common values below |
| `harvester_type_specific_configuration` | dict | Config specific to harvester_type (at minimum `{}`) |
| `default_owner` | int | User PK for default resource owner |
| `harvest_new_resources_by_default` | bool | Auto-harvest new resources |
| `delete_orphan_resources_automatically` | bool | Auto-delete resources no longer found on remote |
| `check_availability_frequency` | int | Minutes between availability checks (>= 0) |
| `harvesting_session_update_frequency` | int | Minutes between harvest sessions (>= 0) |
| `refresh_harvestable_resources_update_frequency` | int | Minutes between refresh sessions (>= 0) |
| `last_check_harvestable_resources_message` | str | Message from last check |

Common `harvester_type` values:
- `"geonode.harvesting.harvesters.geonodeharvester.GeonodeUnifiedHarvesterWorker"` — harvest from another GeoNode
- `"geonode.harvesting.harvesters.wms.OgcWmsHarvester"` — harvest from OGC WMS
- `"geonode.harvesting.harvesters.arcgis.ArcgisHarvesterWorker"` — harvest from ArcGIS

### User Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | str | Required. 150 chars max. Letters, digits, @/./+/-/_ only |
| `password` | str | User password (create only) |
| `email` | str | Email address (max 254 chars) |
| `first_name` | str | First name (max 150 chars) |
| `last_name` | str | Last name (max 150 chars) |
| `is_superuser` | bool | Grant all permissions without explicit assignment |
| `is_staff` | bool | Allow access to admin site |

### Upload Size Limit Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `slug` | str | Identifier (3-255 chars, alphanumeric/hyphens/underscores) |
| `description` | str | Limit description (max 255 chars, nullable) |
| `max_size` | int | Maximum file size in bytes |

### Upload Parallelism Limit Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | str | Limit description (max 255 chars, nullable) |
| `max_number` | int | Maximum parallel uploads (0-32767) |

### Permissions Structure

Used by `set_resource_permissions()`, `patch_resource_permissions()`, and `set_dataset_permissions()`:

```python
{
    "users": {
        "admin": ["view_resourcebase", "download_resourcebase", "change_resourcebase"],
        "viewer": ["view_resourcebase"],
    },
    "groups": {
        "my-group": ["view_resourcebase", "download_resourcebase"],
    },
}
```

Common permission strings: `view_resourcebase`, `download_resourcebase`, `change_resourcebase`, `change_resourcebase_metadata`, `change_resourcebase_permissions`, `publish_resourcebase`.

### Extra Metadata Structure

Used by `add_extra_metadata()` and `update_extra_metadata()`:

```python
[{"metadata_type": "doi", "metadata_value": "10.1234/test"}]
```

### Usage Examples

```python
from cli_anything.geonode.core.client import GeoNodeClient

client = GeoNodeClient(url="https://maps.eurac.edu", token="your-token")

# Create a map with layers
client.create_map(
    title="My Map",
    abstract="A test map",
    category="environment",
    is_published=True,
    keywords="climate,roads",
    maplayers=[
        {
            "name": "geonode:my_dataset",
            "order": 0,
            "visibility": True,
            "opacity": 1.0,
            "current_style": "default",
            "extra_params": {},
        },
    ],
)

# Update a dataset
client.update_dataset(
    42,
    title="Updated Dataset",
    abstract="New description",
    keywords="climate,temperature",
    license="cc-by-4.0",
    spatial_representation_type="vector",
    extent={"coords": [10.4, 46.2, 12.9, 47.2], "srid": "EPSG:4326"},
)

# Set permissions on a resource
client.set_resource_permissions(42, {
    "users": {"admin": ["view_resourcebase", "change_resourcebase"]},
    "groups": {"public": ["view_resourcebase"]},
})

# Create a harvester
client.create_harvester(
    name="WMS Harvester",
    remote_url="https://example.com/geoserver/wms",
    harvester_type="geonode.harvesting.harvesters.wms.OgcWmsHarvester",
    scheduling_enabled=True,
    harvesting_session_update_frequency=60,
    harvester_type_specific_configuration={},
)

# Additional unlisted fields can be passed via **kwargs
client.create_map(title="My Map", some_future_field="value")
```

## Data Model

- **Dataset** — GIS vector/raster data (formerly "Layer")
- **Map** — Collection of datasets as a web map
- **Document** — PDF, image, or other file attached to the catalog
- **GeoApp** — Custom web application
- **ResourceBase** — Abstract parent of all resource types

## Testing

- **142 unit tests** — all client methods mocked, no GeoNode required
- **15 E2E tests** — require a running GeoNode instance with API access
- **6 subprocess tests** — verify installed CLI binary works

## References

- GeoNode docs: https://docs.geonode.org/
- API v2: `{geonode_url}/api/v2/` (OpenAPI schema at `/api/v2/schema/`)
- Source: https://github.com/GeoNode/geonode
