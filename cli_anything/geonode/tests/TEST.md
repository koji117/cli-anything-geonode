# Test Plan — cli-anything-geonode

## Test Inventory

- `test_core.py`: ~30 unit tests (mocked HTTP, no GeoNode required)
- `test_full_e2e.py`: ~15 E2E tests (requires running GeoNode instance)

## Unit Test Plan (`test_core.py`)

### TestConfig (5 tests)
- `test_load_default_config` — returns defaults when no config file exists
- `test_save_and_load_config` — round-trip save/load
- `test_set_url` — URL persists correctly
- `test_set_token` — token and auth_type persist
- `test_show_config_masks_secrets` — password and token are masked

### TestSession (5 tests)
- `test_create_session` — default values
- `test_serialize_round_trip` — to_dict/from_dict
- `test_save_and_load` — file persistence
- `test_record_action` — history tracking
- `test_status` — status dict format

### TestGeoNodeClient (6 tests)
- `test_url_construction` — API URL building with trailing slashes
- `test_token_auth_header` — Bearer token in headers
- `test_basic_auth` — username/password auth
- `test_connection_error` — raises GeoNodeError on connection failure
- `test_api_error` — raises GeoNodeError on 4xx/5xx
- `test_paginated_get` — auto-pagination with multiple pages

### TestDatasetOperations (4 tests)
- `test_list_datasets` — mocked list response
- `test_get_dataset` — mocked detail response
- `test_update_dataset` — mocked PATCH
- `test_delete_dataset` — mocked DELETE

### TestUpload (3 tests)
- `test_upload_dataset` — mocked multipart POST
- `test_poll_upload_complete` — polling returns on COMPLETE
- `test_poll_upload_failed` — raises on FAILED state

### TestCLI (4 tests)
- `test_help` — --help exits 0
- `test_version` — --version shows 1.0.0
- `test_config_show` — config show outputs JSON in --json mode
- `test_dataset_list_json` — --json dataset list (connection error expected)

### TestCLISubprocess (3 tests)
- `test_help_subprocess` — cli-anything-geonode --help via subprocess
- `test_version_subprocess` — --version via subprocess
- `test_config_show_subprocess` — config show via subprocess

## E2E Test Plan (`test_full_e2e.py`)

**Prerequisites:** Running GeoNode instance (docker compose up -d)

### TestConnection (1 test)
- `test_connection` — verify API is reachable

### TestDatasetCRUD (3 tests)
- `test_list_datasets` — list returns paginated response
- `test_upload_and_delete_geojson` — upload GeoJSON, verify in list, delete
- `test_dataset_permissions` — get permissions on a dataset

### TestMapCRUD (2 tests)
- `test_list_maps` — list returns response
- `test_create_and_delete_map` — create, verify, delete

### TestDocumentCRUD (2 tests)
- `test_list_documents` — list returns response
- `test_upload_and_delete_document` — upload PDF, verify, delete

### TestResourceSearch (2 tests)
- `test_list_resources` — unified resource list
- `test_search_resources` — text search returns results

### TestUserGroup (2 tests)
- `test_list_users` — admin user exists
- `test_list_groups` — groups list returns response

### TestFullWorkflow (1 test)
- `test_upload_search_cleanup` — upload dataset → search → verify → delete

### TestCLISubprocessE2E (2 tests)
- `test_dataset_list_json` — subprocess JSON dataset list
- `test_resource_search_json` — subprocess JSON resource search

## Realistic Workflow Scenarios

### Scenario 1: Dataset Publication
**Simulates:** GIS analyst uploading and publishing spatial data
**Operations:** config set-url → config set-token → dataset upload → dataset info → dataset permissions → dataset list
**Verified:** Upload completes, dataset appears in list, permissions are set

### Scenario 2: Map Creation from Datasets
**Simulates:** Creating a web map from existing datasets
**Operations:** dataset list → map create → map info → map layers → map delete
**Verified:** Map is created with correct metadata

### Scenario 3: Document Management
**Simulates:** Attaching supplementary documents to the catalog
**Operations:** document upload → document list → document info → document delete
**Verified:** Document appears in catalog, metadata is correct

---

## Test Results

### Unit Tests (`test_core.py`) — 2025-03-15

```
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/kojisaruya/IdeaProjects/geonode/agent-harness

cli_anything/geonode/tests/test_core.py::TestConfig::test_load_default_config PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_save_and_load_config PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_set_url PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_set_token PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_show_config_masks_secrets PASSED
cli_anything/geonode/tests/test_core.py::TestSession::test_create_session PASSED
cli_anything/geonode/tests/test_core.py::TestSession::test_serialize_round_trip PASSED
cli_anything/geonode/tests/test_core.py::TestSession::test_save_and_load PASSED
cli_anything/geonode/tests/test_core.py::TestSession::test_record_action PASSED
cli_anything/geonode/tests/test_core.py::TestSession::test_status PASSED
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_url_construction PASSED
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_token_auth_header PASSED
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_basic_auth PASSED
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_connection_error PASSED
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_api_error PASSED
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_list_datasets_mocked PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_list_datasets PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_get_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_update_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_delete_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_upload_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_poll_upload_complete PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_poll_upload_failed PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_version PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_config_show PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_dataset_list_json_connection_error PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_version PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_config_show PASSED

============================== 30 passed in 0.29s ==============================
```

### Summary

| Suite | Tests | Passed | Failed | Time |
|-------|-------|--------|--------|------|
| Unit (test_core.py) | 30 | 30 | 0 | 0.29s |
| E2E (test_full_e2e.py) | 15 | — | — | (requires running GeoNode) |

### Coverage Notes

- All core modules tested: config, session, client, CLI commands
- HTTP interactions fully mocked in unit tests
- Subprocess tests verify installed CLI binary works
- E2E tests require a running GeoNode instance (not run in this pass)
