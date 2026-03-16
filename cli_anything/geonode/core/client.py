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
    """Client for GeoNode REST API v2 — 100% endpoint coverage.

    Example::

        # Using environment variables (GEONODE_URL, GEONODE_TOKEN)
        client = GeoNodeClient()

        # Explicit URL + token
        client = GeoNodeClient(url="https://maps.eurac.edu", token="your-token")

        # Basic auth
        client = GeoNodeClient(url="http://localhost:8000", username="admin", password="admin")
    """

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

    @staticmethod
    def _build_payload(explicit, extras):
        """Merge explicit params (dropping None) with extras."""
        payload = {k: v for k, v in explicit.items() if v is not None}
        payload.update(extras)
        return payload

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
        """List datasets with optional filters.

        Example::

            # Basic listing
            client.list_datasets()

            # With filters
            client.list_datasets(page=2, page_size=5, search="temperature")
            client.list_datasets(category__identifier="environment")
            client.list_datasets(owner__username="admin")
        """
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("datasets", params=params)
        return resp.json()

    def get_dataset(self, pk):
        """Get dataset details by ID.

        Example::

            dataset = client.get_dataset(42)
            print(dataset["title"], dataset["alternate"])
        """
        resp = self._get(f"datasets/{pk}")
        return resp.json().get("dataset", resp.json())

    def update_dataset(
        self,
        pk,
        *,
        # Essential
        title=None, abstract=None,
        # Classification
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        # Dataset-specific
        ptype=None, ows_url=None, has_elevation=None, has_time=None,
        is_mosaic=None, elevation_regex=None, time_regex=None,
        featureinfo_custom_template=None, data=None, metadata=None,
        # Dates
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        # Description
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        # Spatial
        srid=None, spatial_representation_type=None, extent=None,
        # Publishing
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        # Misc
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        # Contact roles
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Partial update dataset metadata (PATCH).

        Args:
            title: Dataset title.
            abstract: Dataset description.
            ptype: Processing type (max 255 chars).
            ows_url: OWS service URL for this layer (max 200 chars).
            has_elevation: Whether dataset has elevation data.
            has_time: Whether dataset has time dimension.
            is_mosaic: Whether dataset is a mosaic.
            elevation_regex: Regex for elevation extraction (max 128 chars).
            featureinfo_custom_template: Custom GetFeatureInfo HTML template.
            category: Category identifier string, e.g. "environment", "climatologyMeteorologyAtmosphere".
            group: Group name or identifier.
            keywords: Comma-separated string or list, e.g. "climate,water".
            regions: Region codes, e.g. "ITA".
            license: License identifier, e.g. "cc-by-4.0", "public_domain", "not_specified".
            restriction_code_type: Access restriction, e.g. "otherRestrictions".
            spatial_representation_type: e.g. "vector", "grid".
            extent: Dict with "coords" [minx, miny, maxx, maxy] and "srid", e.g.
                {"coords": [10.4, 46.2, 12.9, 47.2], "srid": "EPSG:4326"}.
            srid: Native spatial reference, e.g. "EPSG:32632".
            poc: Point of contact — list of user PKs.
            metadata_author: Metadata author — list of user PKs.
            maintenance_frequency: e.g. "asNeeded", "daily", "annually".
            **kwargs: Additional fields forwarded to the API.

        Example::

            client.update_dataset(
                42,
                title="Updated Temperature Data",
                abstract="Daily temperature readings for Bolzano 2024",
                keywords="climate,temperature,bolzano",
                category="climatologyMeteorologyAtmosphere",
                license="cc-by-4.0",
                spatial_representation_type="vector",
                srid="EPSG:32632",
                extent={"coords": [11.3, 46.4, 11.5, 46.6], "srid": "EPSG:4326"},
                poc=[1060],
                is_published=True,
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"datasets/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def replace_dataset(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        ptype=None, ows_url=None, has_elevation=None, has_time=None,
        is_mosaic=None, elevation_regex=None, time_regex=None,
        featureinfo_custom_template=None, data=None, metadata=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Full update dataset (PUT)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._put(f"datasets/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def delete_dataset(self, pk):
        """Delete a dataset.

        Example::

            client.delete_dataset(42)  # returns {"pk": 42, "deleted": True}
        """
        self._delete(f"datasets/{pk}")
        return {"pk": pk, "deleted": True}

    def upload_dataset_metadata(self, pk, xml_file_path):
        """Upload ISO metadata XML for a dataset (PUT).

        Example::

            client.upload_dataset_metadata(42, "/path/to/metadata.xml")
        """
        with open(xml_file_path, "rb") as f:
            resp = self._put(f"datasets/{pk}/metadata", files={"metadata_file": f})
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
        """Set dataset permissions.

        Args:
            pk: Dataset ID.
            perms: Dict with "users" and/or "groups" keys. Each maps an
                identifier to a list of permission strings.

        Example::

            client.set_dataset_permissions(42, {
                "users": {
                    "admin": ["view_resourcebase", "download_resourcebase",
                              "change_resourcebase"],
                    "viewer": ["view_resourcebase"],
                },
                "groups": {
                    "public": ["view_resourcebase"],
                },
            })
        """
        resp = self._put(f"datasets/{pk}/permissions", json=perms)
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Maps
    # ═══════════════════════════════════════════════════════════════════════

    def list_maps(self, page=1, page_size=10, **filters):
        """List maps with optional filters.

        Example::

            client.list_maps()
            client.list_maps(search="road", page_size=20)
        """
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("maps", params=params)
        return resp.json()

    def get_map(self, pk):
        """Get map details by ID.

        Example::

            map_data = client.get_map(5)
            print(map_data["title"], map_data["maplayers"])
        """
        resp = self._get(f"maps/{pk}")
        return resp.json().get("map", resp.json())

    def create_map(
        self,
        *,
        # Essential
        title=None, abstract=None,
        # Classification
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        # Map-specific
        maplayers=None, urlsuffix=None, featuredurl=None,
        # Dates
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        # Description
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        # Spatial
        srid=None, spatial_representation_type=None, extent=None,
        # Publishing
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        # Misc
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        # Contact roles
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Create a new map.

        Args:
            title: Map title.
            abstract: Map description.
            maplayers: List of layer dicts, each with:
                - name (str): Dataset alternate name, e.g. "geonode:my_layer".
                - order (int): Display stacking order (0 = bottom).
                - visibility (bool): Whether layer is visible on load.
                - opacity (float): Layer opacity (0.0–1.0).
                - current_style (str): Active SLD style name.
                - extra_params (dict): MapStore config, e.g. {"msId": "...", "styles": []}.
            urlsuffix: Site URL suffix (max 255 chars).
            featuredurl: Featured map URL (max 255 chars).
            category: Category identifier string, e.g. "environment".
            group: Group name or identifier.
            keywords: Comma-separated string or list, e.g. "climate,water".
            regions: Region codes, e.g. "ITA".
            license: License identifier, e.g. "cc-by-4.0".
            restriction_code_type: Access restriction, e.g. "otherRestrictions".
            spatial_representation_type: e.g. "vector", "grid".
            extent: Dict with "coords" [minx, miny, maxx, maxy] and "srid", e.g.
                {"coords": [10.4, 46.2, 12.9, 47.2], "srid": "EPSG:4326"}.
            srid: Native spatial reference, e.g. "EPSG:32632".
            poc: Point of contact — list of user PKs.
            metadata_author: Metadata author — list of user PKs.
            maintenance_frequency: e.g. "asNeeded", "daily", "annually".
            **kwargs: Additional fields forwarded to the API.

        Example::

            # Minimal map
            client.create_map(title="My Map", abstract="A simple map")

            # Map with layers and metadata
            client.create_map(
                title="Road Vulnerability Map",
                abstract="Betweenness centrality analysis of road networks",
                category="society",
                keywords="vulnerability,roads,transalp",
                license="cc-by-4.0",
                regions="ITA",
                is_published=True,
                maplayers=[
                    {
                        "name": "geonode:road_centrality_data",
                        "order": 0,
                        "visibility": True,
                        "opacity": 1.0,
                        "current_style": "road_vulnerability",
                        "extra_params": {},
                    },
                    {
                        "name": "geonode:admin_boundaries",
                        "order": 1,
                        "visibility": True,
                        "opacity": 0.5,
                        "current_style": "default",
                        "extra_params": {},
                    },
                ],
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("maps", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def update_map(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        maplayers=None, urlsuffix=None, featuredurl=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Partial update map (PATCH).

        Args:
            maplayers: List of layer dicts (see create_map for structure).
            urlsuffix: Site URL suffix (max 255 chars).
            featuredurl: Featured map URL (max 255 chars).
            **kwargs: Additional fields forwarded to the API.

        See create_map for detailed field descriptions.

        Example::

            # Update title and add a layer
            client.update_map(5, title="Updated Map Title")

            # Change layer visibility
            client.update_map(5, maplayers=[
                {"name": "geonode:my_layer", "order": 0, "visibility": False,
                 "opacity": 1.0, "current_style": "default", "extra_params": {}},
            ])
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"maps/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def replace_map(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        maplayers=None, urlsuffix=None, featuredurl=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Full update map (PUT)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._put(f"maps/{pk}", json=self._build_payload(_locals, kwargs))
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
        """Upload a document file (POST).

        Example::

            client.upload_document(
                "/path/to/report.pdf",
                title="Annual Climate Report 2024",
                abstract="Summary of climate observations",
            )
        """
        with open(file_path, "rb") as f:
            files = {"doc_file": f}
            data = {}
            if title:
                data["title"] = title
            if abstract:
                data["abstract"] = abstract
            resp = self._post("documents", files=files, data=data)
        return resp.json()

    def update_document(
        self,
        pk,
        *,
        # Essential
        title=None, abstract=None,
        # Classification
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        # Document-specific
        extension=None, doc_url=None,
        # Dates
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        # Description
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        # Spatial
        srid=None, spatial_representation_type=None, extent=None,
        # Publishing
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        # Misc
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        # Contact roles
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Partial update document (PATCH).

        Args:
            extension: File extension (max 128 chars, nullable).
            doc_url: External document URL (max 512 chars, nullable).
            category: Category identifier string, e.g. "environment".
            keywords: Comma-separated string or list, e.g. "report,climate".
            license: License identifier, e.g. "cc-by-4.0".
            **kwargs: Additional fields forwarded to the API.

        See create_map for detailed descriptions of shared ResourceBase fields.

        Example::

            client.update_document(
                10,
                title="Updated Report",
                doc_url="https://example.com/report-v2.pdf",
                category="environment",
                keywords="climate,report",
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"documents/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def replace_document(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        extension=None, doc_url=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Full update document (PUT)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._put(f"documents/{pk}", json=self._build_payload(_locals, kwargs))
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

    def create_geoapp(
        self,
        *,
        # Essential
        title=None, abstract=None, name=None,
        # Classification
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        # Dates
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        # Description
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        # Spatial
        srid=None, spatial_representation_type=None, extent=None,
        # Publishing
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        # Misc
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        # Contact roles
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Create a new GeoApp.

        Args:
            title: GeoApp title.
            abstract: GeoApp description.
            name: GeoApp name (writable, unlike other resource types).
            category: Category identifier string, e.g. "environment".
            keywords: Comma-separated string or list.
            license: License identifier, e.g. "cc-by-4.0".
            **kwargs: Additional fields forwarded to the API.

        See create_map for detailed descriptions of shared ResourceBase fields.

        Example::

            client.create_geoapp(
                name="climate-dashboard",
                title="Climate Dashboard",
                abstract="Interactive climate data visualization",
                category="climatologyMeteorologyAtmosphere",
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("geoapps", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def update_geoapp(
        self,
        pk,
        *,
        title=None, abstract=None, name=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Partial update geoapp (PATCH)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"geoapps/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def replace_geoapp(
        self,
        pk,
        *,
        title=None, abstract=None, name=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Full update geoapp (PUT)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._put(f"geoapps/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def delete_geoapp(self, pk):
        self._delete(f"geoapps/{pk}")
        return {"pk": pk, "deleted": True}

    # ═══════════════════════════════════════════════════════════════════════
    # Resources (unified — ResourceBase)
    # ═══════════════════════════════════════════════════════════════════════

    def list_resources(self, page=1, page_size=10, **filters):
        """List all resources with optional filters.

        Example::

            # All resources
            client.list_resources(page_size=50)

            # Filtered by type and category
            client.list_resources(resource_type="dataset", category__identifier="environment")
        """
        params = {"page": page, "page_size": page_size, **filters}
        resp = self._get("resources", params=params)
        return resp.json()

    def search_resources(self, query, page=1, page_size=10):
        """Full-text search across all resources.

        Example::

            results = client.search_resources("temperature")
            results = client.search_resources("road vulnerability", page_size=20)
        """
        resp = self._get(
            "resources",
            params={
                "search": query,
                "page": page,
                "page_size": page_size,
            },
        )
        return resp.json()

    def get_resource(self, pk):
        resp = self._get(f"resources/{pk}")
        return resp.json().get("resource", resp.json())

    def create_resource(
        self,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Create a resource (POST)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("resources", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def update_resource(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Partial update resource (PATCH)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"resources/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def replace_resource(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Full update resource (PUT)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._put(f"resources/{pk}", json=self._build_payload(_locals, kwargs))
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
        """Set resource permissions (PUT — replaces all permissions).

        Args:
            pk: Resource ID.
            perms: Dict with "users" and/or "groups" keys. Each maps an
                identifier to a list of permission strings. Example::

                    {"users": {"admin": ["view_resourcebase", "download_resourcebase",
                                         "change_resourcebase"]},
                     "groups": {"my-group": ["view_resourcebase"]}}

                Common permissions: view_resourcebase, download_resourcebase,
                change_resourcebase, change_resourcebase_metadata,
                change_resourcebase_permissions, publish_resourcebase.

        Example::

            client.set_resource_permissions(42, {
                "users": {
                    "admin": ["view_resourcebase", "download_resourcebase",
                              "change_resourcebase"],
                },
                "groups": {
                    "public": ["view_resourcebase"],
                },
            })
        """
        resp = self._put(f"resources/{pk}/permissions", json=perms)
        return resp.json()

    def patch_resource_permissions(self, pk, perms):
        """Patch resource permissions (PATCH — merges with existing).

        Args:
            pk: Resource ID.
            perms: Same format as set_resource_permissions. Only the specified
                users/groups are updated; others are left unchanged.

        Example::

            # Grant download access to a specific user without affecting others
            client.patch_resource_permissions(42, {
                "users": {"newuser": ["view_resourcebase", "download_resourcebase"]},
            })
        """
        resp = self._patch(f"resources/{pk}/permissions", json=perms)
        return resp.json()

    def delete_resource_permissions(self, pk):
        """Remove all permissions from resource."""
        self._delete(f"resources/{pk}/permissions")
        return {"pk": pk, "permissions_cleared": True}

    # ── Resource async operations ──

    def async_create_resource(
        self,
        resource_type,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Create resource asynchronously (returns execution_id).

        Example::

            result = client.async_create_resource(
                "dataset",
                title="Async Dataset",
                abstract="Created asynchronously",
            )
            exec_id = result["execution_id"]
            status = client.get_execution_status(exec_id)
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "resource_type", "kwargs")}
        resp = self._post(f"resources/create/{resource_type}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def async_update_resource(
        self,
        pk,
        *,
        title=None, abstract=None,
        category=None, group=None, keywords=None, tkeywords=None, regions=None,
        license=None, restriction_code_type=None,
        date=None, date_type=None,
        temporal_extent_start=None, temporal_extent_end=None,
        purpose=None, edition=None, maintenance_frequency=None,
        supplemental_information=None, data_quality_statement=None,
        constraints_other=None,
        srid=None, spatial_representation_type=None, extent=None,
        is_published=None, is_approved=None, featured=None,
        advertised=None, metadata_only=None, metadata_uploaded_preserve=None,
        attribution=None, doi=None, language=None, embed_url=None,
        resource_type=None, subtype=None, blob=None,
        popular_count=None, share_count=None, rating=None,
        poc=None, metadata_author=None, processor=None, publisher=None,
        custodian=None, distributor=None, resource_user=None,
        resource_provider=None, originator=None, principal_investigator=None,
        **kwargs,
    ):
        """Update resource asynchronously (returns execution_id)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._put(f"resources/{pk}/update", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def async_delete_resource(self, pk):
        """Delete resource asynchronously (returns execution_id)."""
        self._delete(f"resources/{pk}/delete")
        return {"pk": pk, "async_delete": True}

    def copy_resource(self, pk):
        """Copy/clone resource asynchronously (returns execution_id).

        Example::

            result = client.copy_resource(42)
        """
        resp = self._put(f"resources/{pk}/copy")
        return resp.json()

    # ── Resource listings (filtered) ──

    def list_approved_resources(self, page=1, page_size=10):
        resp = self._get(
            "resources/approved", params={"page": page, "page_size": page_size}
        )
        return resp.json()

    def list_published_resources(self, page=1, page_size=10):
        resp = self._get(
            "resources/published", params={"page": page, "page_size": page_size}
        )
        return resp.json()

    def list_featured_resources(self, page=1, page_size=10):
        resp = self._get(
            "resources/featured", params={"page": page, "page_size": page_size}
        )
        return resp.json()

    def list_favorite_resources(self, page=1, page_size=10):
        """List current user's favorite resources."""
        resp = self._get(
            "resources/favorites", params={"page": page, "page_size": page_size}
        )
        return resp.json()

    def get_resource_types(self):
        """Get available resource types with counts."""
        resp = self._get("resources/resource-types")
        return resp.json()

    # ── Favorites ──

    def add_favorite(self, pk):
        """Add resource to favorites (POST).

        Example::

            client.add_favorite(42)
        """
        resp = self._post(f"resources/{pk}/favorite")
        return resp.json()

    def remove_favorite(self, pk):
        """Remove resource from favorites (DELETE)."""
        self._delete(f"resources/{pk}/favorite")
        return {"pk": pk, "unfavorited": True}

    # ── Thumbnails ──

    def set_thumbnail(self, pk, file_path=None, url=None, base64_data=None):
        """Set resource thumbnail (PUT). Supports file, URL, or base64.

        Example::

            # From a local file
            client.set_thumbnail(42, file_path="/path/to/thumb.png")

            # From a URL
            client.set_thumbnail(42, url="https://example.com/thumb.png")

            # From base64
            client.set_thumbnail(42, base64_data="data:image/png;base64,iVBOR...")
        """
        if file_path:
            with open(file_path, "rb") as f:
                resp = self._put(
                    f"resources/{pk}/set-thumbnail", files={"thumbnail": f}
                )
        elif url:
            resp = self._put(
                f"resources/{pk}/set-thumbnail", json={"thumbnail_url": url}
            )
        elif base64_data:
            resp = self._put(
                f"resources/{pk}/set-thumbnail", json={"thumbnail": base64_data}
            )
        else:
            raise GeoNodeError("Must provide file_path, url, or base64_data")
        return resp.json()

    def set_thumbnail_from_bbox(self, pk, bbox, srid="EPSG:4326"):
        """Set thumbnail from bounding box (POST).

        Args:
            pk: Resource ID.
            bbox: Bounding box as [minx, miny, maxx, maxy], e.g. [-180, -90, 180, 90].
            srid: Spatial reference of the bbox, default "EPSG:4326".

        Example::

            client.set_thumbnail_from_bbox(42, [11.3, 46.4, 11.5, 46.6])
            client.set_thumbnail_from_bbox(42, [11.3, 46.4, 11.5, 46.6], srid="EPSG:32632")
        """
        resp = self._post(
            f"resources/{pk}/set-thumbnail-from-bbox", json={"bbox": bbox, "srid": srid}
        )
        return resp.json()

    # ── Extra metadata ──

    def get_extra_metadata(self, pk):
        """Get extra metadata for a resource."""
        resp = self._get(f"resources/{pk}/extra-metadata")
        return resp.json()

    def add_extra_metadata(self, pk, metadata):
        """Add new extra metadata (POST).

        Args:
            pk: Resource ID.
            metadata: List of dicts, each with "metadata_type" and "metadata_value".

        Example::

            client.add_extra_metadata(42, [
                {"metadata_type": "doi", "metadata_value": "10.1234/test"},
                {"metadata_type": "source", "metadata_value": "satellite"},
            ])
        """
        resp = self._post(f"resources/{pk}/extra-metadata", json=metadata)
        return resp.json()

    def update_extra_metadata(self, pk, metadata):
        """Update extra metadata (PUT — replaces all extra metadata).

        Args:
            pk: Resource ID.
            metadata: List of dicts (same format as add_extra_metadata).
        """
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
        """Add linked resources (POST).

        Args:
            pk: Resource ID.
            linked_pks: List of resource PKs to link, e.g. [2, 3, 15].

        Example::

            client.add_linked_resources(42, [10, 15, 23])
        """
        resp = self._post(
            f"resources/{pk}/linked-resources", json={"target": linked_pks}
        )
        return resp.json()

    def remove_linked_resources(self, pk, linked_pks):
        """Remove linked resources (DELETE).

        Args:
            pk: Resource ID.
            linked_pks: List of resource PKs to unlink, e.g. [2, 3].
        """
        self._delete(f"resources/{pk}/linked-resources", json={"target": linked_pks})
        return {"pk": pk, "unlinked": linked_pks}

    # ── Assets ──

    def upload_asset(self, pk, file_path):
        """Upload and create asset for a resource (POST).

        Example::

            client.upload_asset(42, "/data/supplementary_table.csv")
        """
        with open(file_path, "rb") as f:
            resp = self._post(f"resources/{pk}/assets", files={"asset_file": f})
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

    def create_user(
        self,
        username,
        password,
        *,
        email=None,
        first_name=None,
        last_name=None,
        is_superuser=None,
        is_staff=None,
        **kwargs,
    ):
        """Create a new user (POST).

        Args:
            username: Required. 150 chars max. Letters, digits, @/./+/-/_ only.
            password: User password.
            email: Email address (max 254 chars).
            first_name: First name (max 150 chars).
            last_name: Last name (max 150 chars).
            is_superuser: Grant all permissions without explicit assignment.
            is_staff: Allow access to admin site.
            **kwargs: Additional fields forwarded to the API.

        Example::

            client.create_user(
                "jdoe", "secretpass123",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("users", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def update_user(
        self,
        pk,
        *,
        username=None,
        first_name=None,
        last_name=None,
        email=None,
        is_superuser=None,
        is_staff=None,
        **kwargs,
    ):
        """Partial update user (PATCH).

        Args:
            username: 150 chars max. Letters, digits, @/./+/-/_ only.
            first_name: First name (max 150 chars).
            last_name: Last name (max 150 chars).
            email: Email address (max 254 chars).
            is_superuser: Grant all permissions without explicit assignment.
            is_staff: Allow access to admin site.
            **kwargs: Additional fields forwarded to the API.

        Example::

            client.update_user(1060, first_name="Jane", email="jane@example.com")
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"users/{pk}", json=self._build_payload(_locals, kwargs))
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

    def upload_dataset(
        self, file_path, title=None, abstract=None, category=None, keywords=None
    ):
        """Upload a geospatial dataset file (async via /uploads/upload/).

        Args:
            file_path: Path to a geospatial file (.shp, .geojson, .tif, .gpkg, etc.).
            title: Dataset title (defaults to filename).
            abstract: Dataset description.
            category: Category identifier, e.g. "environment".
            keywords: Comma-separated string or list, e.g. "climate,water" or ["climate", "water"].

        Example::

            # Simple upload
            client.upload_dataset("/data/rivers.geojson")

            # Upload with metadata
            result = client.upload_dataset(
                "/data/temperature.tif",
                title="Temperature Raster 2024",
                abstract="Annual mean temperature",
                category="climatologyMeteorologyAtmosphere",
                keywords=["temperature", "climate", "2024"],
            )
            # Poll until complete
            upload_id = result.get("id")
            if upload_id:
                client.poll_upload(upload_id)
        """
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
                data["keywords"] = (
                    ",".join(keywords) if isinstance(keywords, list) else keywords
                )
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
        """Poll upload status until complete or timeout.

        Example::

            result = client.upload_dataset("/data/rivers.geojson")
            status = client.poll_upload(result["id"], timeout=300, interval=5)
        """
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
        """Create a new import/upload via importer (POST).

        Example::

            client.create_import("/data/buildings.gpkg", store_spatial_files=True)
        """
        with open(file_path, "rb") as f:
            files = {"base_file": f}
            resp = self._post("imports", files=files, data=params)
        return resp.json()

    def get_upload_size_limits(self):
        """Get upload size limit configurations."""
        resp = self._get("upload-size-limits")
        return resp.json()

    def create_upload_size_limit(
        self,
        *,
        slug=None,
        description=None,
        max_size=None,
        **kwargs,
    ):
        """Create new upload size limit.

        Args:
            slug: Identifier (3-255 chars, alphanumeric/hyphens/underscores).
            description: Limit description (max 255 chars, nullable).
            max_size: Maximum file size in bytes.
            **kwargs: Additional fields forwarded to the API.

        Example::

            client.create_upload_size_limit(
                slug="dataset-max-size",
                description="Max upload size for datasets",
                max_size=104857600,  # 100 MB
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("upload-size-limits", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def get_upload_parallelism_limits(self):
        """Get upload parallelism limit configurations."""
        resp = self._get("upload-parallelism-limits")
        return resp.json()

    def create_upload_parallelism_limit(
        self,
        *,
        description=None,
        max_number=None,
        **kwargs,
    ):
        """Create new upload parallelism limit.

        Args:
            description: Limit description (max 255 chars, nullable).
            max_number: Maximum parallel uploads (0-32767).
            **kwargs: Additional fields forwarded to the API.

        Example::

            client.create_upload_parallelism_limit(
                description="Default parallelism",
                max_number=5,
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("upload-parallelism-limits", json=self._build_payload(_locals, kwargs))
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Execution Requests
    # ═══════════════════════════════════════════════════════════════════════

    def list_execution_requests(self, page=1, page_size=10):
        """List execution requests for current user."""
        resp = self._get(
            "executionrequest", params={"page": page, "page_size": page_size}
        )
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

    def create_harvester(
        self,
        *,
        name=None,
        remote_url=None,
        scheduling_enabled=None,
        harvester_type=None,
        harvester_type_specific_configuration=None,
        default_owner=None,
        harvest_new_resources_by_default=None,
        delete_orphan_resources_automatically=None,
        check_availability_frequency=None,
        harvesting_session_update_frequency=None,
        refresh_harvestable_resources_update_frequency=None,
        last_check_harvestable_resources_message=None,
        **kwargs,
    ):
        """Create a new harvester.

        Args:
            name: Harvester name (max 255 chars, required).
            remote_url: Base URL of the remote service to harvest (required).
                e.g. "https://example.com/geoserver/wms".
            scheduling_enabled: Periodically schedule harvesting.
            harvester_type: Harvester class. Common values:
                - "geonode.harvesting.harvesters.geonodeharvester.GeonodeUnifiedHarvesterWorker"
                - "geonode.harvesting.harvesters.wms.OgcWmsHarvester"
                - "geonode.harvesting.harvesters.arcgis.ArcgisHarvesterWorker"
                See GeoNode HARVESTER_CLASSES setting for all options.
            harvester_type_specific_configuration: Config dict specific to the
                harvester_type. At minimum an empty dict {} is required.
            default_owner: User PK for default resource owner.
            harvest_new_resources_by_default: Auto-harvest new resources.
            delete_orphan_resources_automatically: Auto-delete resources no longer
                found on the remote service.
            check_availability_frequency: Minutes between availability checks (int >= 0).
            harvesting_session_update_frequency: Minutes between harvest sessions (int >= 0).
            refresh_harvestable_resources_update_frequency: Minutes between refresh
                sessions (int >= 0).
            **kwargs: Additional fields forwarded to the API.

        Example::

            # Harvest from an OGC WMS service
            client.create_harvester(
                name="EURAC WMS Harvester",
                remote_url="https://edp-portal.eurac.edu/geoserver/wms",
                harvester_type="geonode.harvesting.harvesters.wms.OgcWmsHarvester",
                scheduling_enabled=True,
                check_availability_frequency=10,
                harvesting_session_update_frequency=60,
                refresh_harvestable_resources_update_frequency=30,
                default_owner=1000,
                harvest_new_resources_by_default=True,
                harvester_type_specific_configuration={},
            )

            # Harvest from another GeoNode instance
            client.create_harvester(
                name="Remote GeoNode",
                remote_url="https://other-geonode.org",
                harvester_type="geonode.harvesting.harvesters.geonodeharvester.GeonodeUnifiedHarvesterWorker",
                harvester_type_specific_configuration={},
            )
        """
        _locals = {k: v for k, v in locals().items() if k not in ("self", "kwargs")}
        resp = self._post("harvesters", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def update_harvester(
        self,
        pk,
        *,
        name=None,
        remote_url=None,
        scheduling_enabled=None,
        harvester_type=None,
        harvester_type_specific_configuration=None,
        default_owner=None,
        harvest_new_resources_by_default=None,
        delete_orphan_resources_automatically=None,
        check_availability_frequency=None,
        harvesting_session_update_frequency=None,
        refresh_harvestable_resources_update_frequency=None,
        last_check_harvestable_resources_message=None,
        **kwargs,
    ):
        """Partial update harvester (PATCH)."""
        _locals = {k: v for k, v in locals().items() if k not in ("self", "pk", "kwargs")}
        resp = self._patch(f"harvesters/{pk}", json=self._build_payload(_locals, kwargs))
        return resp.json()

    def get_harvestable_resources(self, harvester_pk, page=1, page_size=10):
        """Get harvestable resources for a harvester."""
        resp = self._get(
            f"harvesters/{harvester_pk}/harvestable-resources",
            params={"page": page, "page_size": page_size},
        )
        return resp.json()

    def update_harvestable_resources(self, harvester_pk, **data):
        """Update harvestable resources selection (PATCH)."""
        resp = self._patch(
            f"harvesters/{harvester_pk}/harvestable-resources", json=data
        )
        return resp.json()

    def list_harvesting_sessions(self, page=1, page_size=10):
        """List harvesting sessions."""
        resp = self._get(
            "harvesting-sessions", params={"page": page, "page_size": page_size}
        )
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
        """Autocomplete users for metadata.

        Example::

            client.autocomplete_users("john")  # search by name/username
        """
        resp = self._get(
            "metadata/autocomplete/users", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_resources(self, query=""):
        """Autocomplete resources for metadata."""
        resp = self._get(
            "metadata/autocomplete/resources", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_regions(self, query=""):
        """Autocomplete regions for metadata."""
        resp = self._get(
            "metadata/autocomplete/regions", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_keywords(self, query=""):
        """Autocomplete hierarchical keywords for metadata."""
        resp = self._get(
            "metadata/autocomplete/hkeywords", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_groups(self, query=""):
        """Autocomplete groups for metadata."""
        resp = self._get(
            "metadata/autocomplete/groups", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_categories(self, query=""):
        """Autocomplete categories for metadata."""
        resp = self._get(
            "metadata/autocomplete/categories", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_licenses(self, query=""):
        """Autocomplete licenses for metadata."""
        resp = self._get(
            "metadata/autocomplete/licenses", params={"q": query} if query else {}
        )
        return resp.json()

    def autocomplete_thesaurus_keywords(self, thesaurus_id, query=""):
        """Autocomplete thesaurus keywords for metadata."""
        resp = self._get(
            f"metadata/autocomplete/thesaurus/{thesaurus_id}/keywords",
            params={"q": query} if query else {},
        )
        return resp.json()

    # ═══════════════════════════════════════════════════════════════════════
    # Facets (Search)
    # ═══════════════════════════════════════════════════════════════════════

    def list_facets(self):
        """List all available facets."""
        resp = self._get("facets")
        return resp.json()

    def get_facet(
        self,
        facet_name,
        page=1,
        page_size=10,
        lang=None,
        topic_contains=None,
        **filters,
    ):
        """Get facet details with topics/options.

        Example::

            # List all available facets
            client.list_facets()

            # Get category facet with counts
            client.get_facet("category")

            # Get keyword facet filtered by text
            client.get_facet("keyword", topic_contains="climate", lang="en")
        """
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
        resp = self._get("tkeywords", params={"page": page, "page_size": page_size})
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
        """Verify an access token.

        Example::

            client.verify_token("eyJhbGciOi...")
        """
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
