# GeoNode CLI Harness — SOP

## What is GeoNode?

GeoNode is an open-source geospatial content management system (CMS) built on Django, GeoDjango, GeoServer, and PostGIS. It enables organizations to share, discover, and manage geospatial data through a web interface.

## Architecture

- **Framework:** Django + GeoDjango + Django REST Framework (dynamic-rest)
- **Database:** PostgreSQL + PostGIS
- **Geospatial services:** GeoServer (WMS/WFS/WCS), pyCSW (catalog)
- **Auth:** OAuth2, API key, session-based, Basic Auth
- **Async tasks:** Celery + RabbitMQ/Redis
- **REST API:** `/api/v2/` with endpoints for datasets, maps, documents, users, groups

## How This CLI Works

Unlike typical cli-anything tools that manipulate local project files and invoke local binaries, GeoNode is a **web application**. This CLI acts as a **REST API client**:

1. Connects to a running GeoNode instance over HTTP
2. Wraps `/api/v2/` endpoints with Click commands
3. Handles authentication (Bearer token or Basic Auth)
4. Supports JSON output mode for AI agent consumption
5. Provides interactive REPL for human users

## Backend Dependency

**GeoNode must be running and accessible.** This is not a local binary dependency — it's a network service dependency. The CLI is useless without a GeoNode instance.

Start GeoNode:
```bash
docker compose up -d
```

## Key API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v2/datasets/` | List datasets |
| `GET /api/v2/datasets/{id}/` | Dataset details |
| `PATCH /api/v2/datasets/{id}/` | Update dataset |
| `DELETE /api/v2/datasets/{id}/` | Delete dataset |
| `POST /uploads/upload/` | Upload dataset (async) |
| `GET /api/v2/maps/` | List maps |
| `POST /api/v2/maps/` | Create map |
| `GET /api/v2/documents/` | List documents |
| `POST /api/v2/documents/` | Upload document |
| `GET /api/v2/resources/` | Unified resource list |
| `GET /api/v2/users/` | List users |
| `GET /api/v2/groups/` | List groups |

## Data Model

- **Dataset** — GIS vector/raster data (formerly "Layer")
- **Map** — Collection of datasets as a web map
- **Document** — PDF, image, or other file attached to the catalog
- **GeoApp** — Custom web application
- **ResourceBase** — Abstract parent of all resource types

## Testing

Unit tests mock HTTP responses and require no running GeoNode.
E2E tests require a running GeoNode instance with API access.

## References

- GeoNode docs: https://docs.geonode.org/
- API v2: `{geonode_url}/api/v2/` (OpenAPI schema at `/api/v2/schema/`)
- Source: https://github.com/GeoNode/geonode
