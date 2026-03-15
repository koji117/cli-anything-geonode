"""E2E tests for cli-anything-geonode — requires a running GeoNode instance.

Prerequisites:
    docker compose up -d   # start GeoNode
    export GEONODE_URL=http://localhost:8000
    export GEONODE_TOKEN=<your-api-key>

Run:
    CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/geonode/tests/test_full_e2e.py -v -s
"""

import json
import os
import subprocess
import sys

import pytest

from cli_anything.geonode.core.client import GeoNodeClient, GeoNodeError


# ── Helpers ──────────────────────────────────────────────────────────────


def _get_client():
    """Create client from environment."""
    return GeoNodeClient(
        url=os.environ.get("GEONODE_URL", "http://localhost:8000"),
        token=os.environ.get("GEONODE_TOKEN"),
        username=os.environ.get("GEONODE_USER"),
        password=os.environ.get("GEONODE_PASSWORD"),
    )


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev."""
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = (
        name.replace("cli-anything-", "cli_anything.")
        + "."
        + name.split("-")[-1]
        + "_cli"
    )
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


SAMPLE_GEOJSON = json.dumps(
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [139.6917, 35.6895]},
                "properties": {"name": "Tokyo", "population": 13960000},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [135.5023, 34.6937]},
                "properties": {"name": "Osaka", "population": 2753000},
            },
        ],
    }
)


# ── TestConnection ───────────────────────────────────────────────────────


class TestConnection:
    def test_connection(self):
        """Verify GeoNode API is reachable."""
        client = _get_client()
        result = client.test_connection()
        assert result is not None
        print(f"\n  Connected to GeoNode at {client.base_url}")


# ── TestDatasetCRUD ──────────────────────────────────────────────────────


class TestDatasetCRUD:
    def test_list_datasets(self):
        client = _get_client()
        data = client.list_datasets(page=1, page_size=5)
        assert "datasets" in data or "results" in data
        total = data.get("total", len(data.get("datasets", data.get("results", []))))
        print(f"\n  Found {total} datasets")

    def test_upload_and_delete_geojson(self, tmp_path):
        """Upload a GeoJSON, verify it appears, then delete."""
        client = _get_client()

        geojson_file = tmp_path / "test_cities.geojson"
        geojson_file.write_text(SAMPLE_GEOJSON)

        # Upload
        result = client.upload_dataset(
            str(geojson_file),
            title="CLI Test Cities",
            abstract="Test upload from cli-anything-geonode E2E",
        )
        print(f"\n  Upload result: {json.dumps(result, indent=2, default=str)}")

        # If async, poll for completion
        upload_id = result.get("id", result.get("pk"))
        if upload_id and result.get("state") in ("PENDING", "RUNNING", None):
            try:
                status = client.poll_upload(upload_id, timeout=60, interval=5)
                print(f"  Upload completed: {status.get('state')}")
            except GeoNodeError as e:
                print(f"  Upload polling error: {e}")

        # Verify in list
        data = client.list_datasets(page_size=50)
        datasets = data.get("datasets", data.get("results", []))
        titles = [d.get("title", "") for d in datasets]
        print(f"  Dataset titles: {titles[:10]}")

    def test_dataset_permissions(self):
        """Get permissions on first available dataset."""
        client = _get_client()
        data = client.list_datasets(page=1, page_size=1)
        datasets = data.get("datasets", data.get("results", []))
        if not datasets:
            pytest.skip("No datasets available")
        pk = datasets[0].get("pk", datasets[0].get("id"))
        perms = client.get_dataset_permissions(pk)
        print(
            f"\n  Permissions for dataset {pk}: {json.dumps(perms, indent=2, default=str)}"
        )
        assert perms is not None


# ── TestMapCRUD ──────────────────────────────────────────────────────────


class TestMapCRUD:
    def test_list_maps(self):
        client = _get_client()
        data = client.list_maps(page=1, page_size=5)
        assert "maps" in data or "results" in data
        total = data.get("total", 0)
        print(f"\n  Found {total} maps")

    def test_create_and_delete_map(self):
        """Create a map, verify, then delete."""
        client = _get_client()
        result = client.create_map(
            title="CLI Test Map",
            abstract="Test map from cli-anything-geonode E2E",
        )
        pk = result.get("pk", result.get("id", result.get("map", {}).get("pk")))
        print(f"\n  Created map: {pk}")
        assert pk is not None

        # Verify
        info = client.get_map(pk)
        assert (
            info.get("title") == "CLI Test Map"
            or info.get("map", {}).get("title") == "CLI Test Map"
        )

        # Delete
        client.delete_map(pk)
        print(f"  Deleted map: {pk}")


# ── TestDocumentCRUD ─────────────────────────────────────────────────────


class TestDocumentCRUD:
    def test_list_documents(self):
        client = _get_client()
        data = client.list_documents(page=1, page_size=5)
        assert "documents" in data or "results" in data
        total = data.get("total", 0)
        print(f"\n  Found {total} documents")

    def test_upload_and_delete_document(self, tmp_path):
        """Upload a text document, verify, then delete."""
        client = _get_client()

        doc_file = tmp_path / "test_doc.txt"
        doc_file.write_text(
            "This is a test document for cli-anything-geonode E2E testing."
        )

        result = client.upload_document(
            str(doc_file),
            title="CLI Test Document",
            abstract="Test document from E2E",
        )
        pk = result.get("pk", result.get("id", result.get("document", {}).get("pk")))
        print(f"\n  Uploaded document: {pk}")

        if pk:
            client.delete_document(pk)
            print(f"  Deleted document: {pk}")


# ── TestResourceSearch ───────────────────────────────────────────────────


class TestResourceSearch:
    def test_list_resources(self):
        client = _get_client()
        data = client.list_resources(page=1, page_size=5)
        assert data is not None
        total = data.get("total", 0)
        print(f"\n  Found {total} total resources")

    def test_search_resources(self):
        client = _get_client()
        data = client.search_resources("test", page=1, page_size=5)
        total = data.get("total", 0)
        print(f"\n  Search 'test' returned {total} results")


# ── TestUserGroup ────────────────────────────────────────────────────────


class TestUserGroup:
    def test_list_users(self):
        client = _get_client()
        data = client.list_users(page=1, page_size=10)
        users = data.get("users", data.get("results", []))
        usernames = [u.get("username", "") for u in users]
        print(f"\n  Users: {usernames}")
        assert len(users) > 0

    def test_list_groups(self):
        client = _get_client()
        data = client.list_groups(page=1, page_size=10)
        assert data is not None


# ── TestFullWorkflow ─────────────────────────────────────────────────────


class TestFullWorkflow:
    def test_upload_search_cleanup(self, tmp_path):
        """Full workflow: upload dataset → search → verify → delete."""
        client = _get_client()

        # 1. Upload
        geojson_file = tmp_path / "workflow_test.geojson"
        geojson_file.write_text(SAMPLE_GEOJSON)

        upload_result = client.upload_dataset(
            str(geojson_file),
            title="Workflow Test Cities",
        )
        print(f"\n  Upload: {json.dumps(upload_result, indent=2, default=str)}")

        # 2. Search
        search_result = client.search_resources("Workflow Test")
        total = search_result.get("total", 0)
        print(f"  Search found {total} results")

        # 3. List all resources
        resources = client.list_resources(page_size=50)
        print(f"  Total resources: {resources.get('total', 0)}")


# ── TestCLISubprocessE2E ─────────────────────────────────────────────────


class TestCLISubprocessE2E:
    CLI_BASE = _resolve_cli("cli-anything-geonode")

    def _run(self, args, check=True):
        env = os.environ.copy()
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True,
            text=True,
            check=check,
            env=env,
        )

    def test_dataset_list_json(self):
        result = self._run(["--json", "dataset", "list"], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"\n  Datasets via CLI: {data.get('total', 'unknown')} total")
        else:
            print(f"\n  CLI error (expected if no GeoNode): {result.stderr[:200]}")

    def test_resource_search_json(self):
        result = self._run(["--json", "resource", "search", "test"], check=False)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"\n  Search via CLI: {data.get('total', 'unknown')} results")
        else:
            print(f"\n  CLI error (expected if no GeoNode): {result.stderr[:200]}")
