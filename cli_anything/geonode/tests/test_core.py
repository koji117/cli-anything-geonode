"""Unit tests for cli-anything-geonode — no GeoNode instance required."""

import json
import os
import sys
import subprocess
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from cli_anything.geonode.core.config import (
    load_config, save_config, set_url, set_token, set_credentials,
    show_config, CONFIG_FILE,
)
from cli_anything.geonode.core.session import Session
from cli_anything.geonode.core.client import GeoNodeClient, GeoNodeError
from cli_anything.geonode.geonode_cli import cli


# ── Shared mock helpers ──────────────────────────────────────────────────

def _mock_response(status=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status
    mock.reason = "OK"
    mock.text = json.dumps(json_data or {})
    mock.json.return_value = json_data or {}
    return mock


def _make_client():
    return GeoNodeClient(url="http://geo.test", token="test-token")


# ── TestConfig ───────────────────────────────────────────────────────────

class TestConfig:
    def test_load_default_config(self, tmp_path):
        with patch("cli_anything.geonode.core.config.CONFIG_FILE", tmp_path / "nope.json"):
            config = load_config()
        assert config["url"] == "http://localhost:8000"
        assert config["auth_type"] == "token"
        assert config["token"] is None

    def test_save_and_load_config(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch("cli_anything.geonode.core.config.CONFIG_FILE", cfg_file), \
             patch("cli_anything.geonode.core.config.CONFIG_DIR", tmp_path):
            save_config({"url": "http://example.com", "token": "abc123",
                         "auth_type": "token", "username": None, "password": None})
            loaded = load_config()
        assert loaded["url"] == "http://example.com"
        assert loaded["token"] == "abc123"

    def test_set_url(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch("cli_anything.geonode.core.config.CONFIG_FILE", cfg_file), \
             patch("cli_anything.geonode.core.config.CONFIG_DIR", tmp_path):
            result = set_url("http://geonode.example.com/")
        assert result["url"] == "http://geonode.example.com"

    def test_set_token(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch("cli_anything.geonode.core.config.CONFIG_FILE", cfg_file), \
             patch("cli_anything.geonode.core.config.CONFIG_DIR", tmp_path):
            result = set_token("my-secret-token-1234567890")
        assert result["token"] == "my-secret-token-1234567890"
        assert result["auth_type"] == "token"

    def test_show_config_masks_secrets(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch("cli_anything.geonode.core.config.CONFIG_FILE", cfg_file), \
             patch("cli_anything.geonode.core.config.CONFIG_DIR", tmp_path):
            save_config({"url": "http://x.com", "token": "abcdefghijklmnopqrstuvwxyz",
                         "auth_type": "token", "username": "admin", "password": "secret"})
            display = show_config()
        assert display["password"] == "***"
        assert "..." in display["token"]

    def test_set_credentials(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch("cli_anything.geonode.core.config.CONFIG_FILE", cfg_file), \
             patch("cli_anything.geonode.core.config.CONFIG_DIR", tmp_path):
            result = set_credentials("admin", "geonode")
        assert result["username"] == "admin"
        assert result["auth_type"] == "basic"


# ── TestSession ──────────────────────────────────────────────────────────

class TestSession:
    def test_create_session(self):
        s = Session()
        assert s.url == "http://localhost:8000"
        assert s.auth_type == "token"
        assert s.history == []

    def test_serialize_round_trip(self):
        s = Session(url="http://geo.test", token="tok123")
        d = s.to_dict()
        s2 = Session.from_dict(d)
        assert s2.url == "http://geo.test"
        assert s2.token == "tok123"

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "session.json"
        s = Session(url="http://geo.test", username="admin")
        s.save(str(path))
        s2 = Session.load(str(path))
        assert s2.url == "http://geo.test"
        assert s2.username == "admin"

    def test_record_action(self):
        s = Session()
        s.record_action("list_datasets", {"page": 1}, result={"total": 5})
        assert len(s.history) == 1
        assert s.history[0]["action"] == "list_datasets"

    def test_status(self):
        s = Session(url="http://geo.test", username="admin")
        status = s.status()
        assert status["url"] == "http://geo.test"
        assert status["username"] == "admin"
        assert status["actions"] == 0


# ── TestGeoNodeClient ────────────────────────────────────────────────────

class TestGeoNodeClient:
    def test_url_construction(self):
        c = GeoNodeClient(url="http://geo.test")
        assert c._url("datasets") == "http://geo.test/api/v2/datasets/"
        assert c._url("/datasets/") == "http://geo.test/api/v2/datasets/"

    def test_token_auth_header(self):
        c = GeoNodeClient(url="http://geo.test", token="my-token")
        assert c.session.headers["Authorization"] == "Bearer my-token"

    def test_basic_auth(self):
        c = GeoNodeClient(url="http://geo.test", username="admin", password="pass")
        assert c.session.auth == ("admin", "pass")

    def test_connection_error(self):
        c = GeoNodeClient(url="http://localhost:19999")
        with pytest.raises(GeoNodeError, match="Cannot connect"):
            c.test_connection()

    def test_api_error(self):
        c = GeoNodeClient(url="http://geo.test")
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.reason = "Not Found"
        mock_resp.text = "not found"
        with patch.object(c.session, "request", return_value=mock_resp):
            with pytest.raises(GeoNodeError, match="404"):
                c._get("nonexistent")

    def test_list_datasets_mocked(self):
        c = _make_client()
        resp = _mock_response(json_data={
            "datasets": [{"pk": 1, "title": "Test"}], "total": 1})
        with patch.object(c.session, "request", return_value=resp):
            data = c.list_datasets()
        assert data["total"] == 1
        assert data["datasets"][0]["pk"] == 1

    def test_env_var_defaults(self):
        with patch.dict(os.environ, {"GEONODE_URL": "http://env.test",
                                      "GEONODE_TOKEN": "env-tok"}):
            c = GeoNodeClient()
        assert c.base_url == "http://env.test"
        assert c.token == "env-tok"


# ── TestDatasetOperations ────────────────────────────────────────────────

class TestDatasetOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_datasets(self):
        resp = _mock_response(json_data={"datasets": [{"pk": 1}, {"pk": 2}], "total": 2})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_datasets()
        assert len(data["datasets"]) == 2

    def test_get_dataset(self):
        resp = _mock_response(json_data={
            "dataset": {"pk": 1, "title": "Rivers", "owner": {"username": "admin"}}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_dataset(1)
        assert data["title"] == "Rivers"

    def test_update_dataset(self):
        resp = _mock_response(json_data={"pk": 1, "title": "Updated"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_dataset(1, title="Updated")
        assert data["title"] == "Updated"

    def test_replace_dataset(self):
        resp = _mock_response(json_data={"pk": 1, "title": "Replaced"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.replace_dataset(1, title="Replaced")
        assert data["title"] == "Replaced"

    def test_delete_dataset(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_dataset(1)
        assert data["deleted"] is True

    def test_get_dataset_permissions(self):
        resp = _mock_response(json_data={"users": {"admin": ["view"]}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_dataset_permissions(1)
        assert "users" in data

    def test_set_dataset_permissions(self):
        resp = _mock_response(json_data={"status": "ok"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.set_dataset_permissions(1, {"users": {"admin": ["view"]}})
        assert data["status"] == "ok"

    def test_get_dataset_maplayers(self):
        resp = _mock_response(json_data={"maplayers": []})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_dataset_maplayers(1)
        assert "maplayers" in data

    def test_get_dataset_maps(self):
        resp = _mock_response(json_data={"maps": [{"pk": 10}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_dataset_maps(1)
        assert "maps" in data

    def test_upload_dataset_metadata(self, tmp_path):
        xml = tmp_path / "meta.xml"
        xml.write_text("<metadata/>")
        resp = _mock_response(json_data={"status": "ok"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.upload_dataset_metadata(1, str(xml))
        assert data["status"] == "ok"


# ── TestMapOperations ────────────────────────────────────────────────────

class TestMapOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_maps(self):
        resp = _mock_response(json_data={"maps": [{"pk": 1}], "total": 1})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_maps()
        assert data["total"] == 1

    def test_get_map(self):
        resp = _mock_response(json_data={"map": {"pk": 1, "title": "My Map"}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_map(1)
        assert data["title"] == "My Map"

    def test_create_map(self):
        resp = _mock_response(json_data={"pk": 5, "title": "New Map"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.create_map(title="New Map")
        assert data["pk"] == 5

    def test_update_map(self):
        resp = _mock_response(json_data={"pk": 1, "title": "Updated"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_map(1, title="Updated")
        assert data["title"] == "Updated"

    def test_delete_map(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_map(1)
        assert data["deleted"] is True

    def test_get_map_layers(self):
        resp = _mock_response(json_data={"maplayers": [{"pk": 1}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_map_layers(1)
        assert "maplayers" in data

    def test_get_map_datasets(self):
        resp = _mock_response(json_data={"datasets": [{"pk": 1}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_map_datasets(1)
        assert "datasets" in data


# ── TestDocumentOperations ───────────────────────────────────────────────

class TestDocumentOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_documents(self):
        resp = _mock_response(json_data={"documents": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_documents()
        assert data["total"] == 0

    def test_get_document(self):
        resp = _mock_response(json_data={"document": {"pk": 1, "title": "Report"}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_document(1)
        assert data["title"] == "Report"

    def test_upload_document(self, tmp_path):
        doc = tmp_path / "test.txt"
        doc.write_text("hello")
        resp = _mock_response(json_data={"pk": 10, "title": "test.txt"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.upload_document(str(doc), title="My Doc")
        assert data["pk"] == 10

    def test_delete_document(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_document(1)
        assert data["deleted"] is True

    def test_get_document_linked_resources(self):
        resp = _mock_response(json_data={"linked_to": [{"pk": 2}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_document_linked_resources(1)
        assert "linked_to" in data


# ── TestGeoAppOperations ─────────────────────────────────────────────────

class TestGeoAppOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_geoapps(self):
        resp = _mock_response(json_data={"geoapps": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_geoapps()
        assert data["total"] == 0

    def test_get_geoapp(self):
        resp = _mock_response(json_data={"geoapp": {"pk": 1, "title": "App"}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_geoapp(1)
        assert data["title"] == "App"

    def test_create_geoapp(self):
        resp = _mock_response(json_data={"pk": 3, "title": "New App"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.create_geoapp(title="New App")
        assert data["pk"] == 3

    def test_delete_geoapp(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_geoapp(1)
        assert data["deleted"] is True


# ── TestResourceOperations ───────────────────────────────────────────────

class TestResourceOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_resources(self):
        resp = _mock_response(json_data={"resources": [{"pk": 1}], "total": 1})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_resources()
        assert data["total"] == 1

    def test_search_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.search_resources("test")
        assert data["total"] == 0

    def test_get_resource(self):
        resp = _mock_response(json_data={"resource": {"pk": 1, "title": "R"}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_resource(1)
        assert data["title"] == "R"

    def test_copy_resource(self):
        resp = _mock_response(json_data={"execution_id": "abc-123"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.copy_resource(1)
        assert "execution_id" in data

    def test_delete_resource(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_resource(1)
        assert data["deleted"] is True

    def test_get_resource_permissions(self):
        resp = _mock_response(json_data={"users": {}, "groups": {}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_resource_permissions(1)
        assert "users" in data

    def test_set_resource_permissions(self):
        resp = _mock_response(json_data={"status": "ok"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.set_resource_permissions(1, {"users": {}})
        assert data["status"] == "ok"

    def test_delete_resource_permissions(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_resource_permissions(1)
        assert data["permissions_cleared"] is True

    def test_list_approved_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_approved_resources()
        assert "total" in data

    def test_list_published_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_published_resources()
        assert "total" in data

    def test_list_featured_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_featured_resources()
        assert "total" in data

    def test_list_favorite_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_favorite_resources()
        assert "total" in data

    def test_add_favorite(self):
        resp = _mock_response(json_data={"pk": 1, "favorited": True})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.add_favorite(1)
        assert data["favorited"] is True

    def test_remove_favorite(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.remove_favorite(1)
        assert data["unfavorited"] is True

    def test_get_resource_types(self):
        resp = _mock_response(json_data={"resource_types": [{"name": "dataset", "count": 5}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_resource_types()
        assert "resource_types" in data

    def test_set_thumbnail_url(self):
        resp = _mock_response(json_data={"thumbnail_url": "http://example.com/t.png"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.set_thumbnail(1, url="http://example.com/t.png")
        assert "thumbnail_url" in data

    def test_set_thumbnail_no_args_raises(self):
        with pytest.raises(GeoNodeError, match="Must provide"):
            self.client.set_thumbnail(1)

    def test_set_thumbnail_from_bbox(self):
        resp = _mock_response(json_data={"status": "ok"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.set_thumbnail_from_bbox(1, [-180, -90, 180, 90])
        assert data["status"] == "ok"

    def test_get_extra_metadata(self):
        resp = _mock_response(json_data={"extra": [{"key": "val"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_extra_metadata(1)
        assert "extra" in data

    def test_update_extra_metadata(self):
        resp = _mock_response(json_data={"status": "ok"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_extra_metadata(1, {"key": "val"})
        assert data["status"] == "ok"

    def test_delete_extra_metadata(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_extra_metadata(1)
        assert data["extra_metadata_deleted"] is True

    def test_get_iso_metadata_xml(self):
        resp = _mock_response(json_data={"xml": "<metadata/>"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_iso_metadata_xml(1)
        assert "xml" in data

    def test_get_linked_resources(self):
        resp = _mock_response(json_data={"linked": [{"pk": 2}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_linked_resources(1)
        assert "linked" in data

    def test_add_linked_resources(self):
        resp = _mock_response(json_data={"status": "ok"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.add_linked_resources(1, [2, 3])
        assert data["status"] == "ok"

    def test_remove_linked_resources(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.remove_linked_resources(1, [2])
        assert data["unlinked"] == [2]

    def test_upload_asset(self, tmp_path):
        f = tmp_path / "asset.png"
        f.write_bytes(b"\x89PNG")
        resp = _mock_response(json_data={"asset_id": 99})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.upload_asset(1, str(f))
        assert data["asset_id"] == 99

    def test_delete_asset(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_asset(1, 99)
        assert data["deleted"] is True

    def test_async_create_resource(self):
        resp = _mock_response(json_data={"execution_id": "exec-1"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.async_create_resource("dataset", title="Async")
        assert data["execution_id"] == "exec-1"

    def test_async_delete_resource(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.async_delete_resource(1)
        assert data["async_delete"] is True


# ── TestUserOperations ───────────────────────────────────────────────────

class TestUserOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_users(self):
        resp = _mock_response(json_data={"users": [{"pk": 1, "username": "admin"}], "total": 1})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_users()
        assert data["total"] == 1

    def test_get_user(self):
        resp = _mock_response(json_data={"pk": 1, "username": "admin"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_user(1)
        assert data["username"] == "admin"

    def test_create_user(self):
        resp = _mock_response(json_data={"pk": 5, "username": "newuser"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.create_user("newuser", "pass123", email="u@test.com")
        assert data["username"] == "newuser"

    def test_update_user(self):
        resp = _mock_response(json_data={"pk": 1, "first_name": "Updated"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_user(1, first_name="Updated")
        assert data["first_name"] == "Updated"

    def test_delete_user(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_user(1)
        assert data["deleted"] is True

    def test_get_user_info(self):
        resp = _mock_response(json_data={"username": "admin", "is_superuser": True})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_user_info()
        assert data["username"] == "admin"

    def test_get_roles(self):
        resp = _mock_response(json_data={"roles": ["admin", "member"]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_roles()
        assert "roles" in data


# ── TestGroupOperations ──────────────────────────────────────────────────

class TestGroupOperations:
    def setup_method(self):
        self.client = _make_client()

    def test_list_groups(self):
        resp = _mock_response(json_data={"groups": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_groups()
        assert data["total"] == 0

    def test_get_group(self):
        resp = _mock_response(json_data={"pk": 1, "title": "Editors"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_group(1)
        assert data["title"] == "Editors"

    def test_get_group_members(self):
        resp = _mock_response(json_data={"members": [{"username": "admin"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_group_members(1)
        assert "members" in data

    def test_get_group_managers(self):
        resp = _mock_response(json_data={"managers": [{"username": "admin"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_group_managers(1)
        assert "managers" in data

    def test_get_group_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_group_resources(1)
        assert "total" in data


# ── TestUpload ───────────────────────────────────────────────────────────

class TestUpload:
    def setup_method(self):
        self.client = _make_client()

    def test_upload_dataset(self, tmp_path):
        geojson = tmp_path / "test.geojson"
        geojson.write_text('{"type":"FeatureCollection","features":[]}')
        resp = _mock_response(json_data={"id": 42, "state": "PENDING"})
        with patch.object(self.client.session, "post", return_value=resp):
            data = self.client.upload_dataset(str(geojson), title="Test Upload")
        assert data["id"] == 42

    def test_poll_upload_complete(self):
        resp = _mock_response(json_data={"id": 42, "state": "COMPLETE"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.poll_upload(42, timeout=5, interval=0.1)
        assert data["state"] == "COMPLETE"

    def test_poll_upload_failed(self):
        resp = _mock_response(json_data={"id": 42, "state": "FAILED"})
        with patch.object(self.client.session, "request", return_value=resp):
            with pytest.raises(GeoNodeError, match="failed"):
                self.client.poll_upload(42, timeout=5, interval=0.1)

    def test_list_uploads(self):
        resp = _mock_response(json_data={"uploads": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_uploads()
        assert data["total"] == 0

    def test_list_imports(self):
        resp = _mock_response(json_data={"imports": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_imports()
        assert "total" in data

    def test_get_upload_size_limits(self):
        resp = _mock_response(json_data={"limits": [{"slug": "default", "max_size": 104857600}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_upload_size_limits()
        assert "limits" in data

    def test_get_upload_parallelism_limits(self):
        resp = _mock_response(json_data={"limits": [{"slug": "default", "max_number": 5}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_upload_parallelism_limits()
        assert "limits" in data


# ── TestExecutionRequests ────────────────────────────────────────────────

class TestExecutionRequests:
    def setup_method(self):
        self.client = _make_client()

    def test_list_execution_requests(self):
        resp = _mock_response(json_data={"requests": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_execution_requests()
        assert "total" in data

    def test_get_execution_request(self):
        resp = _mock_response(json_data={"exec_id": "abc", "status": "finished"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_execution_request("abc")
        assert data["status"] == "finished"

    def test_get_execution_status(self):
        resp = _mock_response(json_data={"status": "running", "progress": 50})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_execution_status("abc")
        assert data["status"] == "running"

    def test_delete_execution_request(self):
        resp = _mock_response(status=204)
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_execution_request("abc")
        assert data["deleted"] is True


# ── TestHarvesters ───────────────────────────────────────────────────────

class TestHarvesters:
    def setup_method(self):
        self.client = _make_client()

    def test_list_harvesters(self):
        resp = _mock_response(json_data={"harvesters": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_harvesters()
        assert "total" in data

    def test_get_harvester(self):
        resp = _mock_response(json_data={"pk": 1, "name": "WMS Harvester"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_harvester(1)
        assert data["name"] == "WMS Harvester"

    def test_create_harvester(self):
        resp = _mock_response(json_data={"pk": 2, "name": "New"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.create_harvester(name="New", remote_url="http://wms.test")
        assert data["pk"] == 2

    def test_update_harvester(self):
        resp = _mock_response(json_data={"pk": 1, "name": "Updated"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_harvester(1, name="Updated")
        assert data["name"] == "Updated"

    def test_get_harvestable_resources(self):
        resp = _mock_response(json_data={"resources": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_harvestable_resources(1)
        assert "total" in data

    def test_list_harvesting_sessions(self):
        resp = _mock_response(json_data={"sessions": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_harvesting_sessions()
        assert "total" in data

    def test_get_harvesting_session(self):
        resp = _mock_response(json_data={"pk": 1, "status": "finished"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_harvesting_session(1)
        assert data["status"] == "finished"


# ── TestMetadata ─────────────────────────────────────────────────────────

class TestMetadata:
    def setup_method(self):
        self.client = _make_client()

    def test_get_metadata_info(self):
        resp = _mock_response(json_data={"endpoints": []})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_metadata_info()
        assert "endpoints" in data

    def test_get_metadata_schema(self):
        resp = _mock_response(json_data={"type": "object", "properties": {}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_metadata_schema()
        assert data["type"] == "object"

    def test_get_metadata_instance(self):
        resp = _mock_response(json_data={"pk": 1, "title": "Test"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_metadata_instance(1)
        assert data["pk"] == 1

    def test_update_metadata_instance(self):
        resp = _mock_response(json_data={"pk": 1, "title": "Updated"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_metadata_instance(1, title="Updated")
        assert data["title"] == "Updated"

    def test_autocomplete_users(self):
        resp = _mock_response(json_data={"results": [{"username": "admin"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.autocomplete_users("adm")
        assert len(data["results"]) == 1

    def test_autocomplete_categories(self):
        resp = _mock_response(json_data={"results": []})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.autocomplete_categories("env")
        assert "results" in data

    def test_autocomplete_thesaurus_keywords(self):
        resp = _mock_response(json_data={"results": []})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.autocomplete_thesaurus_keywords(1, "water")
        assert "results" in data


# ── TestFacets ───────────────────────────────────────────────────────────

class TestFacets:
    def setup_method(self):
        self.client = _make_client()

    def test_list_facets(self):
        resp = _mock_response(json_data={"facets": ["category", "keyword"]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_facets()
        assert "facets" in data

    def test_get_facet(self):
        resp = _mock_response(json_data={
            "name": "category", "topics": [{"key": "env", "count": 5}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_facet("category")
        assert data["name"] == "category"


# ── TestCatalogEndpoints ────────────────────────────────────────────────

class TestCatalogEndpoints:
    def setup_method(self):
        self.client = _make_client()

    def test_list_categories(self):
        resp = _mock_response(json_data={
            "categories": [{"pk": 1, "identifier": "environment"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_categories()
        assert len(data["categories"]) == 1

    def test_get_category(self):
        resp = _mock_response(json_data={"pk": 1, "identifier": "environment"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_category(1)
        assert data["identifier"] == "environment"

    def test_list_regions(self):
        resp = _mock_response(json_data={"regions": [{"pk": 1, "code": "GLO"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_regions()
        assert len(data["regions"]) == 1

    def test_get_region(self):
        resp = _mock_response(json_data={"pk": 1, "code": "GLO", "name": "Global"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_region(1)
        assert data["name"] == "Global"

    def test_list_keywords(self):
        resp = _mock_response(json_data={"keywords": [{"pk": 1, "slug": "water"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_keywords()
        assert len(data["keywords"]) == 1

    def test_get_keyword(self):
        resp = _mock_response(json_data={"pk": 1, "slug": "water", "name": "Water"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_keyword(1)
        assert data["name"] == "Water"

    def test_list_thesaurus_keywords(self):
        resp = _mock_response(json_data={"tkeywords": [], "total": 0})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_thesaurus_keywords()
        assert "total" in data

    def test_list_owners(self):
        resp = _mock_response(json_data={"owners": [{"pk": 1, "username": "admin"}]})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_owners()
        assert len(data["owners"]) == 1

    def test_get_owner(self):
        resp = _mock_response(json_data={"pk": 1, "username": "admin"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_owner(1)
        assert data["username"] == "admin"

    def test_get_openapi_schema(self):
        resp = _mock_response(json_data={"openapi": "3.0.0", "paths": {}})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_openapi_schema()
        assert data["openapi"] == "3.0.0"

    def test_verify_token(self):
        resp = _mock_response(json_data={"valid": True})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.verify_token("some-token")
        assert data["valid"] is True

    def test_get_admin_role(self):
        resp = _mock_response(json_data={"role": "admin"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_admin_role()
        assert data["role"] == "admin"


# ── TestCLI ──────────────────────────────────────────────────────────────

class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "GeoNode" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_config_show(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "config", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "url" in data

    def test_dataset_list_json_connection_error(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--url", "http://localhost:19999",
            "--json", "dataset", "list",
        ])
        assert result.exit_code != 0 or "error" in result.output.lower()

    def test_all_command_groups_in_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        for group in ["config", "dataset", "document", "geoapp", "resource",
                       "user", "group", "upload", "execution", "harvester",
                       "metadata", "facet", "category", "region", "keyword",
                       "owner", "schema", "map"]:
            assert group in result.output, f"Missing command group: {group}"

    def test_geoapp_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["geoapp", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "create" in result.output

    def test_resource_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["resource", "--help"])
        assert result.exit_code == 0
        for cmd in ["approved", "published", "featured", "favorites",
                     "favorite", "types", "set-thumbnail", "extra-metadata",
                     "iso-metadata", "linked-resources", "upload-asset"]:
            assert cmd in result.output, f"Missing resource command: {cmd}"

    def test_harvester_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["harvester", "--help"])
        assert result.exit_code == 0
        assert "harvestable-resources" in result.output

    def test_metadata_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["metadata", "--help"])
        assert result.exit_code == 0
        assert "autocomplete" in result.output

    def test_execution_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["execution", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_user_help_has_crud(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["user", "--help"])
        assert result.exit_code == 0
        for cmd in ["create", "update", "delete", "me"]:
            assert cmd in result.output, f"Missing user command: {cmd}"

    def test_upload_help_has_limits(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["upload", "--help"])
        assert result.exit_code == 0
        assert "size-limits" in result.output
        assert "parallelism-limits" in result.output


# ── TestCLISubprocess ────────────────────────────────────────────────────

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
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-geonode")

    def _run(self, args, check=True):
        return subprocess.run(
            self.CLI_BASE + args,
            capture_output=True, text=True,
            check=check,
        )

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "GeoNode" in result.stdout

    def test_version(self):
        result = self._run(["--version"])
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_config_show(self):
        result = self._run(["--json", "config", "show"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "url" in data

    def test_all_groups_in_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        for group in ["geoapp", "execution", "harvester", "metadata",
                       "facet", "category", "region", "keyword", "owner"]:
            assert group in result.stdout, f"Missing group: {group}"

    def test_geoapp_help_subprocess(self):
        result = self._run(["geoapp", "--help"])
        assert result.returncode == 0
        assert "create" in result.stdout

    def test_resource_help_subprocess(self):
        result = self._run(["resource", "--help"])
        assert result.returncode == 0
        assert "favorites" in result.stdout
