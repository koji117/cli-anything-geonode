# Test Plan & Results — cli-anything-geonode

## Test Inventory

- `test_core.py`: 142 unit tests (mocked HTTP, no GeoNode required)
- `test_full_e2e.py`: 15 E2E tests (requires running GeoNode instance)

## Unit Test Plan (`test_core.py`)

### TestConfig (6 tests)
- `test_load_default_config` — returns defaults when no config file exists
- `test_save_and_load_config` — round-trip save/load
- `test_set_url` — URL persists correctly, trailing slash stripped
- `test_set_token` — token and auth_type persist
- `test_show_config_masks_secrets` — password and token are masked in display
- `test_set_credentials` — username/password persist with auth_type=basic

### TestSession (5 tests)
- `test_create_session` — default values
- `test_serialize_round_trip` — to_dict/from_dict preserves all fields
- `test_save_and_load` — JSON file persistence
- `test_record_action` — history tracking with timestamps
- `test_status` — status dict format

### TestGeoNodeClient (8 tests)
- `test_url_construction` — API URL building with trailing slashes
- `test_token_auth_header` — Bearer token in headers
- `test_basic_auth` — username/password auth tuple
- `test_connection_error` — raises GeoNodeError on connection failure
- `test_api_error` — raises GeoNodeError on 4xx/5xx with status code
- `test_list_datasets_mocked` — mocked list returns correct structure
- `test_env_var_defaults` — GEONODE_URL and GEONODE_TOKEN env vars

### TestDatasetOperations (10 tests)
- `test_list_datasets` — paginated list
- `test_get_dataset` — detail with nested JSON unwrapping
- `test_update_dataset` — PATCH partial update
- `test_replace_dataset` — PUT full update
- `test_delete_dataset` — DELETE returns confirmation
- `test_get_dataset_permissions` — permissions response
- `test_set_dataset_permissions` — PUT permissions
- `test_get_dataset_maplayers` — maplayers using this dataset
- `test_get_dataset_maps` — maps using this dataset
- `test_upload_dataset_metadata` — ISO metadata XML upload

### TestMapOperations (7 tests)
- `test_list_maps` — paginated list
- `test_get_map` — detail with nested unwrapping
- `test_create_map` — POST with title
- `test_update_map` — PATCH partial update
- `test_delete_map` — DELETE confirmation
- `test_get_map_layers` — maplayers in map
- `test_get_map_datasets` — datasets used in map

### TestDocumentOperations (5 tests)
- `test_list_documents` — paginated list
- `test_get_document` — detail with nested unwrapping
- `test_upload_document` — multipart file upload
- `test_delete_document` — DELETE confirmation
- `test_get_document_linked_resources` — linked resources

### TestGeoAppOperations (4 tests)
- `test_list_geoapps` — paginated list
- `test_get_geoapp` — detail with nested unwrapping
- `test_create_geoapp` — POST with title
- `test_delete_geoapp` — DELETE confirmation

### TestResourceOperations (30 tests)
- `test_list_resources` — unified paginated list
- `test_search_resources` — text search query
- `test_get_resource` — detail with nested unwrapping
- `test_copy_resource` — async copy returns execution_id
- `test_delete_resource` — DELETE confirmation
- `test_get_resource_permissions` — permissions with users/groups
- `test_set_resource_permissions` — PUT permissions
- `test_delete_resource_permissions` — clear all permissions
- `test_list_approved_resources` — filtered list
- `test_list_published_resources` — filtered list
- `test_list_featured_resources` — filtered list
- `test_list_favorite_resources` — user favorites
- `test_add_favorite` — POST favorite
- `test_remove_favorite` — DELETE favorite
- `test_get_resource_types` — types with counts
- `test_set_thumbnail_url` — set thumbnail from URL
- `test_set_thumbnail_no_args_raises` — validation error
- `test_set_thumbnail_from_bbox` — set thumbnail from bounding box
- `test_get_extra_metadata` — extra metadata
- `test_update_extra_metadata` — PUT extra metadata
- `test_delete_extra_metadata` — clear extra metadata
- `test_get_iso_metadata_xml` — ISO XML document
- `test_get_linked_resources` — linked resources list
- `test_add_linked_resources` — POST linked resources
- `test_remove_linked_resources` — DELETE linked resources
- `test_upload_asset` — multipart asset upload
- `test_delete_asset` — DELETE asset
- `test_async_create_resource` — async create returns execution_id
- `test_async_delete_resource` — async delete

### TestUserOperations (7 tests)
- `test_list_users` — paginated list
- `test_get_user` — user detail
- `test_create_user` — POST with username/password/email
- `test_update_user` — PATCH partial update
- `test_delete_user` — DELETE confirmation
- `test_get_user_info` — authenticated user info
- `test_get_roles` — available roles

### TestGroupOperations (5 tests)
- `test_list_groups` — paginated list
- `test_get_group` — group detail
- `test_get_group_members` — member list
- `test_get_group_managers` — manager list
- `test_get_group_resources` — resources owned by group

### TestUpload (7 tests)
- `test_upload_dataset` — multipart POST to /uploads/upload/
- `test_poll_upload_complete` — polling returns on COMPLETE state
- `test_poll_upload_failed` — raises on FAILED state
- `test_list_uploads` — paginated upload list
- `test_list_imports` — importer orchestrator imports
- `test_get_upload_size_limits` — size limit config
- `test_get_upload_parallelism_limits` — parallelism limit config

### TestExecutionRequests (4 tests)
- `test_list_execution_requests` — paginated list
- `test_get_execution_request` — detail by exec_id
- `test_get_execution_status` — async operation status
- `test_delete_execution_request` — DELETE confirmation

### TestHarvesters (7 tests)
- `test_list_harvesters` — paginated list
- `test_get_harvester` — harvester detail
- `test_create_harvester` — POST with name/URL
- `test_update_harvester` — PATCH partial update
- `test_get_harvestable_resources` — resources available for harvesting
- `test_list_harvesting_sessions` — session list
- `test_get_harvesting_session` — session detail

### TestMetadata (7 tests)
- `test_get_metadata_info` — endpoints info
- `test_get_metadata_schema` — JSON schema
- `test_get_metadata_instance` — instance for resource
- `test_update_metadata_instance` — PATCH instance
- `test_autocomplete_users` — user autocomplete
- `test_autocomplete_categories` — category autocomplete
- `test_autocomplete_thesaurus_keywords` — thesaurus keyword autocomplete

### TestFacets (2 tests)
- `test_list_facets` — available facets
- `test_get_facet` — facet topics

### TestCatalogEndpoints (12 tests)
- `test_list_categories` — topic categories
- `test_get_category` — category detail
- `test_list_regions` — geographic regions
- `test_get_region` — region detail
- `test_list_keywords` — hierarchical keywords
- `test_get_keyword` — keyword detail
- `test_list_thesaurus_keywords` — thesaurus keywords
- `test_list_owners` — resource owners
- `test_get_owner` — owner detail
- `test_get_openapi_schema` — OpenAPI 3.0 schema
- `test_verify_token` — token verification
- `test_get_admin_role` — admin role info

### TestCLI (11 tests)
- `test_help` — --help exits 0
- `test_version` — --version shows 1.0.0
- `test_config_show` — JSON output mode
- `test_dataset_list_json_connection_error` — graceful connection error
- `test_all_command_groups_in_help` — all 18 groups present
- `test_geoapp_help` — geoapp subcommands
- `test_resource_help` — all resource subcommands present
- `test_harvester_help` — harvester subcommands
- `test_metadata_help` — metadata subcommands
- `test_execution_help` — execution subcommands
- `test_user_help_has_crud` — user create/update/delete/me
- `test_upload_help_has_limits` — upload size-limits/parallelism-limits

### TestCLISubprocess (6 tests)
- `test_help` — --help via subprocess
- `test_version` — --version via subprocess
- `test_config_show` — config show via subprocess
- `test_all_groups_in_help` — all new groups visible
- `test_geoapp_help_subprocess` — geoapp --help
- `test_resource_help_subprocess` — resource --help

## E2E Test Plan (`test_full_e2e.py`)

**Prerequisites:** Running GeoNode instance (`docker compose up -d`)

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
- `test_upload_and_delete_document` — upload text document, verify, delete

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
**Operations:** dataset list → map create → map info → map layers → map datasets → map delete
**Verified:** Map is created with correct metadata, layers/datasets are accessible

### Scenario 3: Document Management
**Simulates:** Attaching supplementary documents to the catalog
**Operations:** document upload → document list → document info → document linked-resources → document delete
**Verified:** Document appears in catalog, metadata and linked resources are correct

### Scenario 4: Resource Discovery & Curation
**Simulates:** Catalog administrator curating featured resources
**Operations:** resource search → resource info → resource favorite → resource favorites → resource set-thumbnail → resource featured
**Verified:** Search returns results, favorites and thumbnails persist

### Scenario 5: Harvesting Remote Services
**Simulates:** Importing datasets from a remote WMS/WFS service
**Operations:** harvester create → harvester harvestable-resources → harvester sessions → execution status
**Verified:** Harvester is created, harvestable resources are listed, sessions tracked

### Scenario 6: Metadata Management
**Simulates:** Metadata librarian updating ISO-compliant metadata
**Operations:** metadata schema → metadata instance → metadata autocomplete → resource iso-metadata → dataset metadata (XML upload)
**Verified:** Schema is valid, metadata updates persist, autocomplete works

---

## Test Results

### Unit Tests (`test_core.py`) — 2026-03-15

```
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/kojisaruya/IdeaProjects/geonode/agent-harness

cli_anything/geonode/tests/test_core.py::TestConfig::test_load_default_config PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_save_and_load_config PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_set_url PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_set_token PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_show_config_masks_secrets PASSED
cli_anything/geonode/tests/test_core.py::TestConfig::test_set_credentials PASSED
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
cli_anything/geonode/tests/test_core.py::TestGeoNodeClient::test_env_var_defaults PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_list_datasets PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_get_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_update_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_replace_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_delete_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_get_dataset_permissions PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_set_dataset_permissions PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_get_dataset_maplayers PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_get_dataset_maps PASSED
cli_anything/geonode/tests/test_core.py::TestDatasetOperations::test_upload_dataset_metadata PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_list_maps PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_get_map PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_create_map PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_update_map PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_delete_map PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_get_map_layers PASSED
cli_anything/geonode/tests/test_core.py::TestMapOperations::test_get_map_datasets PASSED
cli_anything/geonode/tests/test_core.py::TestDocumentOperations::test_list_documents PASSED
cli_anything/geonode/tests/test_core.py::TestDocumentOperations::test_get_document PASSED
cli_anything/geonode/tests/test_core.py::TestDocumentOperations::test_upload_document PASSED
cli_anything/geonode/tests/test_core.py::TestDocumentOperations::test_delete_document PASSED
cli_anything/geonode/tests/test_core.py::TestDocumentOperations::test_get_document_linked_resources PASSED
cli_anything/geonode/tests/test_core.py::TestGeoAppOperations::test_list_geoapps PASSED
cli_anything/geonode/tests/test_core.py::TestGeoAppOperations::test_get_geoapp PASSED
cli_anything/geonode/tests/test_core.py::TestGeoAppOperations::test_create_geoapp PASSED
cli_anything/geonode/tests/test_core.py::TestGeoAppOperations::test_delete_geoapp PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_list_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_search_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_get_resource PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_copy_resource PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_delete_resource PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_get_resource_permissions PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_set_resource_permissions PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_delete_resource_permissions PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_list_approved_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_list_published_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_list_featured_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_list_favorite_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_add_favorite PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_remove_favorite PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_get_resource_types PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_set_thumbnail_url PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_set_thumbnail_no_args_raises PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_set_thumbnail_from_bbox PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_get_extra_metadata PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_update_extra_metadata PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_delete_extra_metadata PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_get_iso_metadata_xml PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_get_linked_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_add_linked_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_remove_linked_resources PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_upload_asset PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_delete_asset PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_async_create_resource PASSED
cli_anything/geonode/tests/test_core.py::TestResourceOperations::test_async_delete_resource PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_list_users PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_get_user PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_create_user PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_update_user PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_delete_user PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_get_user_info PASSED
cli_anything/geonode/tests/test_core.py::TestUserOperations::test_get_roles PASSED
cli_anything/geonode/tests/test_core.py::TestGroupOperations::test_list_groups PASSED
cli_anything/geonode/tests/test_core.py::TestGroupOperations::test_get_group PASSED
cli_anything/geonode/tests/test_core.py::TestGroupOperations::test_get_group_members PASSED
cli_anything/geonode/tests/test_core.py::TestGroupOperations::test_get_group_managers PASSED
cli_anything/geonode/tests/test_core.py::TestGroupOperations::test_get_group_resources PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_upload_dataset PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_poll_upload_complete PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_poll_upload_failed PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_list_uploads PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_list_imports PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_get_upload_size_limits PASSED
cli_anything/geonode/tests/test_core.py::TestUpload::test_get_upload_parallelism_limits PASSED
cli_anything/geonode/tests/test_core.py::TestExecutionRequests::test_list_execution_requests PASSED
cli_anything/geonode/tests/test_core.py::TestExecutionRequests::test_get_execution_request PASSED
cli_anything/geonode/tests/test_core.py::TestExecutionRequests::test_get_execution_status PASSED
cli_anything/geonode/tests/test_core.py::TestExecutionRequests::test_delete_execution_request PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_list_harvesters PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_get_harvester PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_create_harvester PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_update_harvester PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_get_harvestable_resources PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_list_harvesting_sessions PASSED
cli_anything/geonode/tests/test_core.py::TestHarvesters::test_get_harvesting_session PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_get_metadata_info PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_get_metadata_schema PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_get_metadata_instance PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_update_metadata_instance PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_autocomplete_users PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_autocomplete_categories PASSED
cli_anything/geonode/tests/test_core.py::TestMetadata::test_autocomplete_thesaurus_keywords PASSED
cli_anything/geonode/tests/test_core.py::TestFacets::test_list_facets PASSED
cli_anything/geonode/tests/test_core.py::TestFacets::test_get_facet PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_list_categories PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_get_category PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_list_regions PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_get_region PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_list_keywords PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_get_keyword PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_list_thesaurus_keywords PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_list_owners PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_get_owner PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_get_openapi_schema PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_verify_token PASSED
cli_anything/geonode/tests/test_core.py::TestCatalogEndpoints::test_get_admin_role PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_version PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_config_show PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_dataset_list_json_connection_error PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_all_command_groups_in_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_geoapp_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_resource_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_harvester_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_metadata_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_execution_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_user_help_has_crud PASSED
cli_anything/geonode/tests/test_core.py::TestCLI::test_upload_help_has_limits PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_version PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_config_show PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_all_groups_in_help PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_geoapp_help_subprocess PASSED
cli_anything/geonode/tests/test_core.py::TestCLISubprocess::test_resource_help_subprocess PASSED

============================== 142 passed in 0.60s ==============================
```

### Summary

| Suite | Tests | Passed | Failed | Time |
|-------|-------|--------|--------|------|
| Unit (test_core.py) | 142 | 142 | 0 | 0.60s |
| E2E (test_full_e2e.py) | 15 | — | — | (requires running GeoNode) |

### Coverage Notes

- **Client methods:** Every one of ~90 client methods has a dedicated unit test
- **CLI commands:** All 18 command groups verified present in --help
- **Subcommands:** Key subcommands verified for resource, user, upload, harvester, metadata, execution groups
- **Auth modes:** Both token (Bearer) and basic auth tested
- **Error handling:** Connection errors and HTTP 4xx/5xx tested
- **Edge cases:** Missing args (set_thumbnail), env var defaults, trailing slash stripping
- **Subprocess:** Installed CLI binary tested via subprocess (--help, --version, config show, group help)
- **E2E tests:** Require a running GeoNode instance (not run in this pass)
