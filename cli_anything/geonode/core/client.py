"""GeoNode REST API v2 HTTP client."""

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
    """Client for GeoNode REST API v2."""

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

    # ── Connection ──

    def test_connection(self):
        """Test connection to GeoNode and return basic info."""
        resp = self._get("")
        return resp.json()

    # ── Datasets ──

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
        """Update dataset metadata."""
        resp = self._patch(f"datasets/{pk}", json=data)
        return resp.json()

    def delete_dataset(self, pk):
        """Delete a dataset."""
        self._delete(f"datasets/{pk}")
        return {"pk": pk, "deleted": True}

    def get_dataset_permissions(self, pk):
        """Get dataset permissions."""
        resp = self._get(f"datasets/{pk}/permissions")
        return resp.json()

    def set_dataset_permissions(self, pk, perms):
        """Set dataset permissions."""
        resp = self._put(f"datasets/{pk}/permissions", json=perms)
        return resp.json()

    # ── Maps ──

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
        resp = self._patch(f"maps/{pk}", json=data)
        return resp.json()

    def delete_map(self, pk):
        self._delete(f"maps/{pk}")
        return {"pk": pk, "deleted": True}

    def get_map_layers(self, pk):
        resp = self._get(f"maps/{pk}/maplayers")
        return resp.json()

    # ── Documents ──

    def list_documents(self, page=1, page_size=10, **filters):
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("documents", params=params)
        return resp.json()

    def get_document(self, pk):
        resp = self._get(f"documents/{pk}")
        return resp.json().get("document", resp.json())

    def upload_document(self, file_path, title=None, abstract=None):
        """Upload a document file."""
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
        resp = self._patch(f"documents/{pk}", json=data)
        return resp.json()

    def delete_document(self, pk):
        self._delete(f"documents/{pk}")
        return {"pk": pk, "deleted": True}

    # ── Resources (unified) ──

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

    def get_resource_permissions(self, pk):
        resp = self._get(f"resources/{pk}/permissions")
        return resp.json()

    def set_resource_permissions(self, pk, perms):
        resp = self._put(f"resources/{pk}/permissions", json=perms)
        return resp.json()

    def copy_resource(self, pk):
        resp = self._put(f"resources/{pk}/copy")
        return resp.json()

    # ── Users ──

    def list_users(self, page=1, page_size=10):
        resp = self._get("users", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_user(self, pk):
        resp = self._get(f"users/{pk}")
        return resp.json()

    # ── Groups ──

    def list_groups(self, page=1, page_size=10):
        resp = self._get("groups", params={"page": page, "page_size": page_size})
        return resp.json()

    def get_group(self, pk):
        resp = self._get(f"groups/{pk}")
        return resp.json()

    def get_group_members(self, pk):
        resp = self._get(f"groups/{pk}/members")
        return resp.json()

    def get_group_resources(self, pk):
        resp = self._get(f"groups/{pk}/resources")
        return resp.json()

    # ── Uploads ──

    def upload_dataset(self, file_path, title=None, abstract=None,
                       category=None, keywords=None):
        """Upload a geospatial dataset file (async)."""
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

    # ── Categories / Regions / Keywords ──

    def list_categories(self):
        resp = self._get("categories")
        return resp.json()

    def list_regions(self, page=1, page_size=50):
        resp = self._get("regions", params={"page": page, "page_size": page_size})
        return resp.json()

    def list_keywords(self, page=1, page_size=50):
        resp = self._get("keywords", params={"page": page, "page_size": page_size})
        return resp.json()
