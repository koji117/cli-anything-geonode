# GeoNode CLI Harness — SOP

## What is GeoNode?

GeoNode is an open-source geospatial content management system (CMS) built on Django, GeoDjango, GeoServer, and PostGIS. It enables organizations to share, discover, and manage geospatial data through a web interface.

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
