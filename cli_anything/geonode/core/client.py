"""GeoNode REST API v2 HTTP client — complete endpoint coverage."""

import json
import os
import time

import requests


class GeoNodeError(Exception):
    """Error from GeoNode REST API."""
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class GeoNodeClient:
    """Client for GeoNode REST API v2 — 100% endpoint coverage."""

    def __init__(self, url=None, token=None, username=None, password=None):
        self.base_url = (
            url or os.environ.get("GEONODE_URL", "http://localhost:8000")
        ).rstrip("/")
        self.api_url = f"{self.base_url}/api/v2"
        self.token = token or os.environ.get("GEONODE_TOKEN")
        self.username = username or os.environ.get("GEONODE_USER")
        self.password = password or os.environ.get("GEONODE_PASSWORD")

        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        elif self.username and self.password:
            self.session.auth = (self.username, self.password)

    def _url(self, path):
        """Build full API URL."""
        path = path.lstrip("/")
        if not path.endswith("/") and "?" not in path:
            path = f"{path}/"
        return f"{self.api_url}/{path}"

    def _request(self, method, path, raw_url=False, **kwargs):
        """Make HTTP request to GeoNode API."""
        url = path if raw_url else self._url(path)
        try:
            resp = self.session.request(method, url, **kwargs)
        except requests.ConnectionError:
            raise GeoNodeError(
                f"Cannot connect to GeoNode at {self.base_url}\n"
                "Make sure GeoNode is running. Start with:\n"
                "  docker compose up -d\n"
                "Or set GEONODE_URL environment variable."
            )
        if resp.status_code >= 400:
            raise GeoNodeError(
                f"GeoNode API error: {resp.status_code} {resp.reason}",
                status_code=resp.status_code,
                response_text=resp.text[:500] if resp.text else None,
            )
        return resp

    def _get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def _post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def _patch(self, path, **kwargs):
        return self._request("PATCH", path, **kwargs)

    def _put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def _delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)

    def _paginated_get(self, path, page_size=10, max_pages=100, **params):
        """Auto-paginate a DRF list endpoint, yielding all results."""
        params["page_size"] = page_size
        page = 1
        while page <= max_pages:
            params["page"] = page
            resp = self._get(path, params=params)
            data = resp.json()

            resources = data.get("resources", data.get("results", []))
            if isinstance(resources, list):
                yield from resources
            else:
                break

            total = data.get("total", 0)
            if page * page_size >= total:
                break
            page += 1

    # ═══════════════════════════════════════════════════════════════════════
    # Connection
    # ═══════════════════════════════════════════════════════════════════════

    def test_connection(self):
        """Test connection to GeoNode and return basic info."""
        resp = self._get("")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Datasets (Layers)
    # ═══════════════════════════════════════════════════════════════════════

    def list_datasets(self, page=1, page_size=10, **filters):
        """List datasets with optional filters."""
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("datasets", params=params)
        return resp.json()

    def get_dataset(self, pk):
        """Get dataset details by ID."""
        resp = self._get(f"datasets/{pk}")
        return resp.json().get("dataset", resp.json())

    def update_dataset(self, pk, **data):
        """Partial update dataset metadata (PATCH)."""
        resp = self._patch(f"datasets/{pk}", json=data)
        return resp.json()

    def replace_dataset(self, pk, **data):
        """Full update dataset (PUT)."""
        resp = self._put(f"datasets/{pk}", json=data)
        return resp.json()

    def delete_dataset(self, pk):
        """Delete a dataset."""
        self._delete(f"datasets/{pk}")
        return {"pk": pk, "deleted": True}

    def upload_dataset_metadata(self, pk, xml_file_path):
        """Upload ISO metadata XML for a dataset (PUT)."""
        with open(xml_file_path, "rb") as f:
            resp = self._put(f"datasets/{pk}/metadata",
                             files={"metadata_file": f})
        return resp.json()

    def get_dataset_maplayers(self, pk):
        """Get map layers using this dataset."""
        resp = self._get(f"datasets/{pk}/maplayers")
        return resp.json()

    def get_dataset_maps(self, pk):
        """Get maps using this dataset."""
        resp = self._get(f"datasets/{pk}/maps")
        return resp.json()

    def get_dataset_permissions(self, pk):
        """Get dataset permissions."""
        resp = self._get(f"datasets/{pk}/permissions")
        return resp.json()

    def set_dataset_permissions(self, pk, perms):
        """Set dataset permissions."""
        resp = self._put(f"datasets/{pk}/permissions", json=perms)
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Maps
    # ═══════════════════════════════════════════════════════════════════════

    def list_maps(self, page=1, page_size=10, **filters):
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("maps", params=params)
        return resp.json()

    def get_map(self, pk):
        resp = self._get(f"maps/{pk}")
        return resp.json().get("map", resp.json())

    def create_map(self, **data):
        resp = self._post("maps", json=data)
        return resp.json()

    def update_map(self, pk, **data):
        """Partial update map (PATCH)."""
        resp = self._patch(f"maps/{pk}", json=data)
        return resp.json()

    def replace_map(self, pk, **data):
        """Full update map (PUT)."""
        resp = self._put(f"maps/{pk}", json=data)
        return resp.json()

    def delete_map(self, pk):
        self._delete(f"maps/{pk}")
        return {"pk": pk, "deleted": True}

    def get_map_layers(self, pk):
        """Get maplayers in this map."""
        resp = self._get(f"maps/{pk}/maplayers")
        return resp.json()

    def get_map_datasets(self, pk):
        """Get datasets used in this map."""
        resp = self._get(f"maps/{pk}/datasets")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Documents
    # ═══════════════════════════════════════════════════════════════════════

    def list_documents(self, page=1, page_size=10, **filters):
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("documents", params=params)
        return resp.json()

    def get_document(self, pk):
        resp = self._get(f"documents/{pk}")
        return resp.json().get("document", resp.json())

    def upload_document(self, file_path, title=None, abstract=None):
        """Upload a document file (POST)."""
        with open(file_path, "rb") as f:
            files = {"doc_file": f}
            data = {}
            if title:
                data["title"] = title
            if abstract:
                data["abstract"] = abstract
            resp = self._post("documents", files=files, data=data)
        return resp.json()

    def update_document(self, pk, **data):
        """Partial update document (PATCH)."""
        resp = self._patch(f"documents/{pk}", json=data)
        return resp.json()

    def replace_document(self, pk, **data):
        """Full update document (PUT)."""
        resp = self._put(f"documents/{pk}", json=data)
        return resp.json()

    def delete_document(self, pk):
        self._delete(f"documents/{pk}")
        return {"pk": pk, "deleted": True}

    def get_document_linked_resources(self, pk):
        """Get resources linked to a document."""
        resp = self._get(f"documents/{pk}/linked-resources")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # GeoApps
    # ═══════════════════════════════════════════════════════════════════════

    def list_geoapps(self, page=1, page_size=10, **filters):
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("geoapps", params=params)
        return resp.json()

    def get_geoapp(self, pk):
        resp = self._get(f"geoapps/{pk}")
        return resp.json().get("geoapp", resp.json())

    def create_geoapp(self, **data):
        resp = self._post("geoapps", json=data)
        return resp.json()

    def update_geoapp(self, pk, **data):
        """Partial update geoapp (PATCH)."""
        resp = self._patch(f"geoapps/{pk}", json=data)
        return resp.json()

    def replace_geoapp(self, pk, **data):
        """Full update geoapp (PUT)."""
        resp = self._put(f"geoapps/{pk}", json=data)
        return resp.json()

    def delete_geoapp(self, pk):
        self._delete(f"geoapps/{pk}")
        return {"pk": pk, "deleted": True}

    # ═══════════════════════════════════════════════════════════════════════
    # Resources (unified — ResourceBase)
    # ═══════════════════════════════════════════════════════════════════════

    def list_resources(self, page=1, page_size=10, **filters):
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("resources", params=params)
        return resp.json()

    def search_resources(self, query, page=1, page_size=10):
        resp = self._get("resources", params={
            "search": query, "page": page, "page_size": page_size,
        })
        return resp.json()

    def get_resource(self, pk):
        resp = self._get(f"resources/{pk}")
        return resp.json().get("resource", resp.json())

    def create_resource(self, **data):
        """Create a resource (POST)."""
        resp = self._post("resources", json=data)
        return resp.json()

    def update_resource(self, pk, **data):
        """Partial update resource (PATCH)."""
        resp = self._patch(f"resources/{pk}", json=data)
        return resp.json()

    def replace_resource(self, pk, **data):
        """Full update resource (PUT)."""
        resp = self._put(f"resources/{pk}", json=data)
        return resp.json()

    def delete_resource(self, pk):
        """Delete a resource."""
        self._delete(f"resources/{pk}")
        return {"pk": pk, "deleted": True}

    # ── Resource permissions ──

    def get_resource_permissions(self, pk):
        resp = self._get(f"resources/{pk}/permissions")
        return resp.json()

    def set_resource_permissions(self, pk, perms):
        """Set resource permissions (PUT)."""
        resp = self._put(f"resources/{pk}/permissions", json=perms)
        return resp.json()

    def patch_resource_permissions(self, pk, perms):
        """Patch resource permissions (PATCH)."""
        resp = self._patch(f"resources/{pk}/permissions", json=perms)
        return resp.json()

    def delete_resource_permissions(self, pk):
        """Remove all permissions from resource."""
        self._delete(f"resources/{pk}/permissions")
        return {"pk": pk, "permissions_cleared": True}

    # ── Resource async operations ──

    def async_create_resource(self, resource_type, **data):
        """Create resource asynchronously (returns execution_id)."""
        resp = self._post(f"resources/create/{resource_type}", json=data)
        return resp.json()

    def async_update_resource(self, pk, **data):
        """Update resource asynchronously (returns execution_id)."""
        resp = self._put(f"resources/{pk}/update", json=data)
        return resp.json()

    def async_delete_resource(self, pk):
        """Delete resource asynchronously (returns execution_id)."""
        resp = self._delete(f"resources/{pk}/delete")
        return {"pk": pk, "async_delete": True}

    def copy_resource(self, pk):
        """Copy/clone resource asynchronously (returns execution_id)."""
        resp = self._put(f"resources/{pk}/copy")
        return resp.json()

    # ── Resource listings (filtered) ──

    def list_approved_resources(self, page=1, page_size=10):
        resp = self._get("resources/approved", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def list_published_resources(self, page=1, page_size=10):
        resp = self._get("resources/published", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def list_featured_resources(self, page=1, page_size=10):
        resp = self._get("resources/featured", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def list_favorite_resources(self, page=1, page_size=10):
        """List current user's favorite resources."""
        resp = self._get("resources/favorites", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def get_resource_types(self):
        """Get available resource types with counts."""
        resp = self._get("resources/resource-types")
        return resp.json()

    # ── Favorites ──

    def add_favorite(self, pk):
        """Add resource to favorites (POST)."""
        resp = self._post(f"resources/{pk}/favorite")
        return resp.json()

    def remove_favorite(self, pk):
        """Remove resource from favorites (DELETE)."""
        self._delete(f"resources/{pk}/favorite")
        return {"pk": pk, "unfavorited": True}

    # ── Thumbnails ──

    def set_thumbnail(self, pk, file_path=None, url=None, base64_data=None):
        """Set resource thumbnail (PUT). Supports file, URL, or base64."""
        if file_path:
            with open(file_path, "rb") as f:
                resp = self._put(f"resources/{pk}/set-thumbnail",
                                 files={"thumbnail": f})
        elif url:
            resp = self._put(f"resources/{pk}/set-thumbnail",
                             json={"thumbnail_url": url})
        elif base64_data:
            resp = self._put(f"resources/{pk}/set-thumbnail",
                             json={"thumbnail": base64_data})
        else:
            raise GeoNodeError("Must provide file_path, url, or base64_data")
        return resp.json()

    def set_thumbnail_from_bbox(self, pk, bbox, srid="EPSG:4326"):
        """Set thumbnail from bounding box (POST)."""
        resp = self._post(f"resources/{pk}/set-thumbnail-from-bbox",
                          json={"bbox": bbox, "srid": srid})
        return resp.json()

    # ── Extra metadata ──

    def get_extra_metadata(self, pk):
        """Get extra metadata for a resource."""
        resp = self._get(f"resources/{pk}/extra-metadata")
        return resp.json()

    def add_extra_metadata(self, pk, metadata):
        """Add new extra metadata (POST)."""
        resp = self._post(f"resources/{pk}/extra-metadata", json=metadata)
        return resp.json()

    def update_extra_metadata(self, pk, metadata):
        """Update extra metadata (PUT)."""
        resp = self._put(f"resources/{pk}/extra-metadata", json=metadata)
        return resp.json()

    def delete_extra_metadata(self, pk):
        """Delete extra metadata."""
        self._delete(f"resources/{pk}/extra-metadata")
        return {"pk": pk, "extra_metadata_deleted": True}

    # ── ISO metadata XML ──

    def get_iso_metadata_xml(self, pk):
        """Get ISO metadata XML document for a resource."""
        resp = self._get(f"resources/{pk}/iso-metadata-xml")
        return resp.json()

    # ── Linked resources ──

    def get_linked_resources(self, pk):
        """Get linked resources for a resource."""
        resp = self._get(f"resources/{pk}/linked-resources")
        return resp.json()

    def add_linked_resources(self, pk, linked_pks):
        """Add linked resources (POST)."""
        resp = self._post(f"resources/{pk}/linked-resources",
                          json={"target": linked_pks})
        return resp.json()

    def remove_linked_resources(self, pk, linked_pks):
        """Remove linked resources (DELETE)."""
        self._delete(f"resources/{pk}/linked-resources",
                     json={"target": linked_pks})
        return {"pk": pk, "unlinked": linked_pks}

    # ── Assets ──

    def upload_asset(self, pk, file_path):
        """Upload and create asset for a resource (POST)."""
        with open(file_path, "rb") as f:
            resp = self._post(f"resources/{pk}/assets",
                              files={"asset_file": f})
        return resp.json()

    def delete_asset(self, pk, asset_id):
        """Delete asset from resource."""
        self._delete(f"resources/{pk}/assets/{asset_id}")
        return {"pk": pk, "asset_id": asset_id, "deleted": True}

    # ═══════════════════════════════════════════════════════════════════════
    # Users
    # ═══════════════════════════════════════════════════════════════════════

    def list_users(self, page=1, page_size=10):
        resp = self._get("users", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_user(self, pk):
        resp = self._get(f"users/{pk}")
        return resp.json()

    def create_user(self, username, password, email=None, **extra):
        """Create a new user (POST)."""
        data = {"username": username, "password": password, **extra}
        if email:
            data["email"] = email
        resp = self._post("users", json=data)
        return resp.json()

    def update_user(self, pk, **data):
        """Partial update user (PATCH)."""
        resp = self._patch(f"users/{pk}", json=data)
        return resp.json()

    def delete_user(self, pk):
        """Delete a user."""
        self._delete(f"users/{pk}")
        return {"pk": pk, "deleted": True}

    # ═══════════════════════════════════════════════════════════════════════
    # Groups
    # ═══════════════════════════════════════════════════════════════════════

    def list_groups(self, page=1, page_size=10):
        resp = self._get("groups", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_group(self, pk):
        resp = self._get(f"groups/{pk}")
        return resp.json()

    def get_group_members(self, pk):
        resp = self._get(f"groups/{pk}/members")
        return resp.json()

    def get_group_managers(self, pk):
        """Get group managers."""
        resp = self._get(f"groups/{pk}/managers")
        return resp.json()

    def get_group_resources(self, pk):
        resp = self._get(f"groups/{pk}/resources")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Uploads / Imports
    # ═══════════════════════════════════════════════════════════════════════

    def upload_dataset(self, file_path, title=None, abstract=None,
                       category=None, keywords=None):
        """Upload a geospatial dataset file (async via /uploads/upload/)."""
        url = f"{self.base_url}/uploads/upload/"
        with open(file_path, "rb") as f:
            files = {"base_file": f}
            data = {}
            if title:
                data["dataset_title"] = title
            if abstract:
                data["abstract"] = abstract
            if category:
                data["category"] = category
            if keywords:
                data["keywords"] = ",".join(keywords) if isinstance(keywords, list) else keywords
            try:
                resp = self.session.post(url, files=files, data=data)
            except requests.ConnectionError:
                raise GeoNodeError(f"Cannot connect to GeoNode at {self.base_url}")
            if resp.status_code >= 400:
                raise GeoNodeError(
                    f"Upload error: {resp.status_code} {resp.reason}",
                    status_code=resp.status_code,
                    response_text=resp.text[:500] if resp.text else None,
                )
        return resp.json()

    def list_uploads(self, page=1, page_size=10):
        resp = self._get("uploads", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_upload(self, pk):
        resp = self._get(f"uploads/{pk}")
        return resp.json()

    def poll_upload(self, pk, timeout=120, interval=3):
        """Poll upload status until complete or timeout."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_upload(pk)
            state = status.get("state", status.get("status", ""))
            if state in ("COMPLETE", "PROCESSED", "FINISHED"):
                return status
            if state in ("FAILED", "ERROR", "INVALID"):
                raise GeoNodeError(
                    f"Upload {pk} failed: {state}",
                    response_text=json.dumps(status),
                )
            time.sleep(interval)
        raise GeoNodeError(f"Upload {pk} timed out after {timeout}s")

    def list_imports(self, page=1, page_size=10):
        """List imports via the new importer orchestrator."""
        resp = self._get("imports", params={"page": page, "page_size": page_size})
        return resp.json()

    def create_import(self, file_path, **params):
        """Create a new import/upload via importer (POST)."""
        with open(file_path, "rb") as f:
            files = {"base_file": f}
            resp = self._post("imports", files=files, data=params)
        return resp.json()

    def get_upload_size_limits(self):
        """Get upload size limit configurations."""
        resp = self._get("upload-size-limits")
        return resp.json()

    def create_upload_size_limit(self, **data):
        """Create new upload size limit."""
        resp = self._post("upload-size-limits", json=data)
        return resp.json()

    def get_upload_parallelism_limits(self):
        """Get upload parallelism limit configurations."""
        resp = self._get("upload-parallelism-limits")
        return resp.json()

    def create_upload_parallelism_limit(self, **data):
        """Create new upload parallelism limit."""
        resp = self._post("upload-parallelism-limits", json=data)
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Execution Requests
    # ═══════════════════════════════════════════════════════════════════════

    def list_execution_requests(self, page=1, page_size=10):
        """List execution requests for current user."""
        resp = self._get("executionrequest", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def get_execution_request(self, exec_id):
        """Get specific execution request."""
        resp = self._get(f"executionrequest/{exec_id}")
        return resp.json()

    def delete_execution_request(self, exec_id):
        """Delete an execution request."""
        self._delete(f"executionrequest/{exec_id}")
        return {"exec_id": exec_id, "deleted": True}

    def get_execution_status(self, exec_id):
        """Check async operation status."""
        resp = self._get(f"resource-service/execution-status/{exec_id}")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Harvesters
    # ═══════════════════════════════════════════════════════════════════════

    def list_harvesters(self, page=1, page_size=10):
        resp = self._get("harvesters", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_harvester(self, pk):
        resp = self._get(f"harvesters/{pk}")
        return resp.json()

    def create_harvester(self, **data):
        resp = self._post("harvesters", json=data)
        return resp.json()

    def update_harvester(self, pk, **data):
        resp = self._patch(f"harvesters/{pk}", json=data)
        return resp.json()

    def get_harvestable_resources(self, harvester_pk, page=1, page_size=10):
        """Get harvestable resources for a harvester."""
        resp = self._get(f"harvesters/{harvester_pk}/harvestable-resources",
                         params={"page": page, "page_size": page_size})
        return resp.json()

    def update_harvestable_resources(self, harvester_pk, **data):
        """Update harvestable resources selection (PATCH)."""
        resp = self._patch(f"harvesters/{harvester_pk}/harvestable-resources",
                           json=data)
        return resp.json()

    def list_harvesting_sessions(self, page=1, page_size=10):
        """List harvesting sessions."""
        resp = self._get("harvesting-sessions", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def get_harvesting_session(self, pk):
        """Get harvesting session details."""
        resp = self._get(f"harvesting-sessions/{pk}")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Metadata
    # ═══════════════════════════════════════════════════════════════════════

    def get_metadata_info(self):
        """List metadata endpoints info."""
        resp = self._get("metadata")
        return resp.json()

    def get_metadata_schema(self, pk=None):
        """Get JSON schema for metadata."""
        path = f"metadata/schema/{pk}" if pk else "metadata/schema"
        resp = self._get(path)
        return resp.json()

    def get_metadata_instance(self, pk):
        """Get metadata instance for a resource."""
        resp = self._get(f"metadata/instance/{pk}")
        return resp.json()

    def update_metadata_instance(self, pk, **data):
        """Partial update metadata instance (PATCH)."""
        resp = self._patch(f"metadata/instance/{pk}", json=data)
        return resp.json()

    def replace_metadata_instance(self, pk, **data):
        """Full update metadata instance (PUT)."""
        resp = self._put(f"metadata/instance/{pk}", json=data)
        return resp.json()

    def autocomplete_users(self, query=""):
        """Autocomplete users for metadata."""
        resp = self._get("metadata/autocomplete/users",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_resources(self, query=""):
        """Autocomplete resources for metadata."""
        resp = self._get("metadata/autocomplete/resources",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_regions(self, query=""):
        """Autocomplete regions for metadata."""
        resp = self._get("metadata/autocomplete/regions",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_keywords(self, query=""):
        """Autocomplete hierarchical keywords for metadata."""
        resp = self._get("metadata/autocomplete/hkeywords",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_groups(self, query=""):
        """Autocomplete groups for metadata."""
        resp = self._get("metadata/autocomplete/groups",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_categories(self, query=""):
        """Autocomplete categories for metadata."""
        resp = self._get("metadata/autocomplete/categories",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_licenses(self, query=""):
        """Autocomplete licenses for metadata."""
        resp = self._get("metadata/autocomplete/licenses",
                         params={"q": query} if query else {})
        return resp.json()

    def autocomplete_thesaurus_keywords(self, thesaurus_id, query=""):
        """Autocomplete thesaurus keywords for metadata."""
        resp = self._get(
            f"metadata/autocomplete/thesaurus/{thesaurus_id}/keywords",
            params={"q": query} if query else {})
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Facets (Search)
    # ═══════════════════════════════════════════════════════════════════════

    def list_facets(self):
        """List all available facets."""
        resp = self._get("facets")
        return resp.json()

    def get_facet(self, facet_name, page=1, page_size=10, lang=None,
                  topic_contains=None, **filters):
        """Get facet details with topics/options."""
        params = {"page": page, "page_size": page_size, **filters}
        if lang:
            params["lang"] = lang
        if topic_contains:
            params["topic_contains"] = topic_contains
        resp = self._get(f"facets/{facet_name}", params=params)
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Categories / Regions / Keywords / Thesaurus Keywords / Owners
    # ═══════════════════════════════════════════════════════════════════════

    def list_categories(self, page=1, page_size=50):
        resp = self._get("categories", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_category(self, pk):
        resp = self._get(f"categories/{pk}")
        return resp.json()

    def list_regions(self, page=1, page_size=50):
        resp = self._get("regions", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_region(self, pk):
        resp = self._get(f"regions/{pk}")
        return resp.json()

    def list_keywords(self, page=1, page_size=50):
        resp = self._get("keywords", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_keyword(self, pk):
        resp = self._get(f"keywords/{pk}")
        return resp.json()

    def list_thesaurus_keywords(self, page=1, page_size=50):
        """List thesaurus keywords."""
        resp = self._get("tkeywords", params={
            "page": page, "page_size": page_size})
        return resp.json()

    def get_thesaurus_keyword(self, pk):
        """Get thesaurus keyword details."""
        resp = self._get(f"tkeywords/{pk}")
        return resp.json()

    def list_owners(self, page=1, page_size=50):
        """List resource owners."""
        resp = self._get("owners", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_owner(self, pk):
        """Get owner details."""
        resp = self._get(f"owners/{pk}")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Schema / Documentation
    # ═══════════════════════════════════════════════════════════════════════

    def get_openapi_schema(self):
        """Get OpenAPI/drf-spectacular schema."""
        resp = self._get("schema")
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Auth / User Info (non-standard endpoints)
    # ═══════════════════════════════════════════════════════════════════════

    def get_user_info(self):
        """Get authenticated user information."""
        resp = self._get("user-info")
        return resp.json()

    def verify_token(self, token):
        """Verify an access token."""
        resp = self._post("verify-token", json={"token": token})
        return resp.json()

    def get_roles(self):
        """Get available roles."""
        resp = self._get("roles")
        return resp.json()

    def get_admin_role(self):
        """Get admin role info."""
        resp = self._get("admin-role")
        return resp.json()
