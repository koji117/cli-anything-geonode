"""Unit tests for cli-anything-geonode — no GeoNode instance required."""

import json
import os
import sys
import subprocess
import tempfile
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
        c = GeoNodeClient(url="http://geo.test")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "datasets": [{"pk": 1, "title": "Test"}],
            "total": 1,
        }
        with patch.object(c.session, "request", return_value=mock_resp):
            data = c.list_datasets()
        assert data["total"] == 1
        assert data["datasets"][0]["pk"] == 1


# ── TestDatasetOperations ────────────────────────────────────────────────

class TestDatasetOperations:
    def setup_method(self):
        self.client = GeoNodeClient(url="http://geo.test")

    def _mock_response(self, status=200, json_data=None):
        mock = MagicMock()
        mock.status_code = status
        mock.reason = "OK"
        mock.text = json.dumps(json_data or {})
        mock.json.return_value = json_data or {}
        return mock

    def test_list_datasets(self):
        resp = self._mock_response(json_data={
            "datasets": [{"pk": 1}, {"pk": 2}], "total": 2,
        })
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.list_datasets()
        assert len(data["datasets"]) == 2

    def test_get_dataset(self):
        resp = self._mock_response(json_data={
            "dataset": {"pk": 1, "title": "Rivers", "owner": {"username": "admin"}},
        })
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.get_dataset(1)
        assert data["title"] == "Rivers"

    def test_update_dataset(self):
        resp = self._mock_response(json_data={"pk": 1, "title": "Updated"})
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.update_dataset(1, title="Updated")
        assert data["title"] == "Updated"

    def test_delete_dataset(self):
        resp = self._mock_response(status=204, json_data={})
        resp.status_code = 204
        with patch.object(self.client.session, "request", return_value=resp):
            data = self.client.delete_dataset(1)
        assert data["deleted"] is True


# ── TestUpload ───────────────────────────────────────────────────────────

class TestUpload:
    def setup_method(self):
        self.client = GeoNodeClient(url="http://geo.test", token="tok")

    def _mock_response(self, status=200, json_data=None):
        mock = MagicMock()
        mock.status_code = status
        mock.reason = "OK"
        mock.text = json.dumps(json_data or {})
        mock.json.return_value = json_data or {}
        return mock

    def test_upload_dataset(self, tmp_path):
        geojson = tmp_path / "test.geojson"
        geojson.write_text('{"type":"FeatureCollection","features":[]}')
        resp = self._mock_response(json_data={"id": 42, "state": "PENDING"})
        with patch.object(self.client.session, "post", return_value=resp):
            data = self.client.upload_dataset(str(geojson), title="Test Upload")
        assert data["id"] == 42

    def test_poll_upload_complete(self):
        resp_complete = self._mock_response(json_data={"id": 42, "state": "COMPLETE"})
        with patch.object(self.client.session, "request", return_value=resp_complete):
            data = self.client.poll_upload(42, timeout=5, interval=0.1)
        assert data["state"] == "COMPLETE"

    def test_poll_upload_failed(self):
        resp_failed = self._mock_response(json_data={"id": 42, "state": "FAILED"})
        with patch.object(self.client.session, "request", return_value=resp_failed):
            with pytest.raises(GeoNodeError, match="failed"):
                self.client.poll_upload(42, timeout=5, interval=0.1)


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
        # Should exit with error (connection refused)
        assert result.exit_code != 0 or "error" in result.output.lower()


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
