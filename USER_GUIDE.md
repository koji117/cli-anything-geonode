# GeoNode User Guide — Web Interface

## 1. Introduction

GeoNode is an open-source geospatial content management system (CMS) for creating, sharing, and collaboratively managing spatial data. Built on Django, GeoServer, and PostGIS, it provides a web-based platform where organizations can publish datasets, create interactive maps, upload documents, and build geospatial applications.

**Who this guide is for:** Data managers, GIS analysts, researchers, and administrators who use GeoNode through a web browser.

**What this guide covers:** Day-to-day tasks in the GeoNode web interface — from uploading your first dataset to managing permissions and harvesting remote services. For API/CLI documentation, see [README.md](README.md).

**GeoNode version:** This guide targets GeoNode 4.x. Some features or layouts may differ on older versions.

---

## 2. Getting Started

### 2.1 Logging In

1. Navigate to your organization's GeoNode URL (e.g. `https://maps.example.com`).
2. Click **Sign In** in the top-right corner.
3. Enter your username and password, then click **Sign In**.
4. If you don't have an account, click **Register** (if self-registration is enabled) or contact your GeoNode administrator.

> **Tip:** GeoNode supports multiple authentication methods. Your organization may use LDAP, OAuth2 (Google, GitHub), or SAML single sign-on instead of username/password.

### 2.2 The Dashboard

After logging in, the home page shows:

- **Search bar** — Full-text search across all resources at the top.
- **Resource cards** — Recently added or featured datasets, maps, and documents.
- **Navigation menu** — Top bar with links to **Datasets**, **Maps**, **Documents**, **GeoApps**, **People**, **Groups**.
- **User menu** — Top-right dropdown with your profile, favorites, and sign-out.

### 2.3 Your Profile

1. Click your username in the top-right corner and select **Profile**.
2. On your profile page you can:
   - Edit your **name**, **organization**, **position**, and **bio**.
   - Upload a **profile picture**.
   - View your **activity feed** — recent uploads, edits, and comments.
   - See all resources you own.

### 2.4 Navigation Overview

| Menu Item | What It Shows |
|-----------|---------------|
| **Datasets** | All published vector and raster datasets (layers) |
| **Maps** | Interactive web maps composed of datasets |
| **Documents** | Uploaded files — PDFs, images, reports, spreadsheets |
| **GeoApps** | Custom web applications and dashboards |
| **People** | Registered users and their profiles |
| **Groups** | Organizational groups with shared resources |

---

## 3. Discovering Resources

### 3.1 Browsing Resources

Click **Datasets**, **Maps**, **Documents**, or **GeoApps** in the navigation menu to see a filterable list of resources. Each resource card shows:

- **Thumbnail** — Map preview or document icon.
- **Title** and **abstract** excerpt.
- **Owner** — Who uploaded/created it.
- **Category** — Topic classification.
- **Date** — When it was created or last updated.

Click any card to open the resource detail page.

### 3.2 Faceted Search

On any resource listing page, the left sidebar provides faceted filters:

- **Resource Type** — Dataset, Map, Document, GeoApp.
- **Category** — Topic categories like Environment, Transportation, Society, Climatology.
- **Region** — Geographic regions (continent, country, sub-region hierarchy).
- **Keyword** — Tags assigned by data owners.
- **Owner** — Filter by who created the resource.
- **Date Range** — Filter by creation or temporal coverage dates.
- **Extent** — Draw a bounding box on the map to find resources in a geographic area.

Select multiple filters to narrow results. Filters combine with AND logic.

### 3.3 Full-Text Search

Use the search bar at the top of any page to search across titles, abstracts, keywords, and metadata. The search is case-insensitive and supports partial matching.

> **Tip:** Combine search text with faceted filters for precise results. For example, search "temperature" and then filter by Category = "Climatology" and Region = "Europe".

### 3.4 Resource Detail Page

Every resource has a detail page with:

- **Map preview** — Interactive map viewer for spatial resources (datasets, maps).
- **Info panel** — Title, abstract, owner, category, keywords, license, dates.
- **Metadata tab** — Full ISO-compliant metadata including contact information, spatial extent, temporal coverage, and quality statements.
- **Download options** — Available formats for downloading the data.
- **Linked resources** — Related datasets, maps, or documents.
- **Share** — Permalink and social sharing options.
- **Comments** — Discussion thread (if enabled).

### 3.5 Favorites

To bookmark a resource for quick access:

1. On any resource detail page, click the **star icon** or **Add to Favorites**.
2. Access your favorites from the user menu: click your username → **Favorites**.

---

## 4. Working with Datasets

Datasets (also called "layers") are the core content type in GeoNode. They represent geospatial vector or raster data published through GeoServer.

### 4.1 Supported Formats

| Format | Type | Notes |
|--------|------|-------|
| **Shapefile** | Vector | Must be zipped (.zip containing .shp, .shx, .dbf, .prj at minimum) |
| **GeoTIFF** | Raster | Recommended for raster data; supports CRS embedding |
| **GeoJSON** | Vector | Single JSON file; good for small to medium datasets |
| **GeoPackage** | Vector/Raster | SQLite-based; supports multiple layers in one file |
| **CSV** | Tabular/Vector | Must include latitude/longitude columns for spatial mapping |
| **KML/KMZ** | Vector | Google Earth format |

### 4.2 Uploading a Dataset

1. Click **Datasets** in the navigation menu.
2. Click the **Upload Dataset** button (top-right).
3. **Drag and drop** your file(s) into the upload area, or click **Browse** to select files.
   - For Shapefiles, upload the entire .zip file.
   - For GeoTIFF, upload the .tif file directly.
4. GeoNode validates the file and shows format detection.
5. Click **Upload** to start processing.
6. A progress indicator shows the async upload status. Processing includes:
   - File validation and format detection.
   - Coordinate reference system (CRS) detection.
   - Publishing to GeoServer.
   - Generating a thumbnail preview.
7. Once complete, you're redirected to the dataset detail page.

> **Tip:** Check your organization's upload size limits. Administrators can configure maximum file sizes per resource type. If your file is too large, consider using GeoPackage or cloud-optimized GeoTIFF.

### 4.3 Viewing a Dataset

On the dataset detail page:

- The **map viewer** shows the data with its default style.
- Click **Attribute Table** (or the table icon) to view and search feature attributes.
- The **Info** panel shows layer metadata, CRS, extent, and feature count.
- Use map controls to pan, zoom, and identify features by clicking.

### 4.4 Editing Metadata

Good metadata makes your data discoverable and understandable. To edit:

1. On the dataset detail page, click the **Edit** button (pencil icon) or **Metadata** → **Edit**.
2. Fill in the metadata form:

| Field | Description | Example |
|-------|-------------|---------|
| **Title** | Clear, descriptive name | "Road Network — Province of Bolzano 2024" |
| **Abstract** | What the data represents, source, coverage | "Vector dataset of all classified roads..." |
| **Category** | ISO topic category | Environment, Transportation, Society |
| **Regions** | Geographic coverage areas | Italy, South Tyrol, Europe |
| **Keywords** | Discoverable tags | roads, infrastructure, transportation |
| **Thesaurus Keywords** | Controlled vocabulary terms | Selected from INSPIRE or other thesauri |
| **License** | Usage license | Creative Commons Attribution 4.0 |
| **Date** | Reference date | 2024-01-15 (creation, publication, or revision) |
| **Temporal Extent** | Time period the data covers | Start: 2020-01-01, End: 2024-12-31 |
| **Language** | Data language | English, Italian, German |
| **Purpose** | Why the data was created | "Supports regional transportation planning" |
| **Supplemental Info** | Additional context | Processing methods, known limitations |
| **Data Quality** | Quality statement | Positional accuracy, completeness notes |
| **Spatial Representation** | Data geometry type | Vector, Grid (raster) |
| **Restriction** | Access restrictions | Copyright, license, other restrictions |

3. Under **Contact Roles**, assign responsible parties:
   - **Point of Contact** — Primary contact for questions about the data.
   - **Metadata Author** — Who wrote the metadata.
   - **Processor**, **Publisher**, **Custodian**, **Distributor** — Additional roles as needed.

4. Click **Save** to update the metadata.

> **Tip:** At minimum, always fill in **Title**, **Abstract**, **Category**, and **Keywords**. These are the fields most used in search and discovery.

### 4.5 Managing Styles

Styles control how a dataset is rendered on maps. GeoNode uses SLD (Styled Layer Descriptor) for styling.

1. On the dataset detail page, click **Styles** (or the paint palette icon).
2. View the current **default style** and any **associated styles**.
3. To change the default style, select a different style from the dropdown.
4. To upload a custom SLD:
   - Click **Upload Style**.
   - Select your `.sld` file.
   - Give it a name and click **Save**.

### 4.6 Downloading a Dataset

1. On the dataset detail page, click **Download**.
2. Choose from available formats:
   - **Original** — The format it was uploaded in.
   - **Shapefile** — Zipped shapefile.
   - **GeoJSON** — JSON format.
   - **GML** — Geography Markup Language (XML).
   - **CSV** — Comma-separated values (attributes only for vector).
   - **GeoTIFF** — For raster datasets.
   - **KML** — Google Earth format.
3. The download starts automatically.

### 4.7 Elevation and Time Dimensions

Some datasets have elevation (e.g., depth, altitude) or time dimensions:

- **Time dimension** — Enables temporal animation in the map viewer. The time slider lets you step through time steps or animate.
- **Elevation dimension** — Allows selecting specific depth/altitude levels.

These are configured by the dataset owner or administrator through the dataset's **Dimensions** settings.

### 4.8 Version and Asset Management

- **Replacing a dataset** — Upload a new version of the data file to update the dataset in-place, preserving its metadata, permissions, and any maps that reference it.
- **Assets** — Additional files attached to a dataset (supplementary documentation, processing scripts, auxiliary data). Manage these from the **Assets** section on the detail page.

---

## 5. Creating and Editing Maps

Maps in GeoNode are interactive web maps built by combining one or more datasets as layers. The map editor is powered by **MapStore**.

### 5.1 Creating a New Map

**From scratch:**
1. Click **Maps** in the navigation menu.
2. Click **Create Map** (top-right).
3. The MapStore editor opens with an empty map and a default basemap.

**From a dataset:**
1. On any dataset detail page, click **Create Map**.
2. The editor opens with that dataset already added as a layer.

### 5.2 The MapStore Map Viewer

MapStore provides a full-featured map interface:

| Tool | Description |
|------|-------------|
| **Pan** | Click and drag to move the map |
| **Zoom** | Scroll wheel, or use +/- buttons |
| **Identify** | Click a feature to see its attributes in a popup |
| **Measure** | Measure distance (line) or area (polygon) on the map |
| **Basemap** | Switch between OpenStreetMap, satellite imagery, and other basemaps |
| **Print** | Export the current map view as PDF |
| **Share** | Generate a permalink or embed code |

### 5.3 Adding Layers to a Map

1. In the map editor, click the **Layers** panel (layer stack icon).
2. Click **Add Layer** (+).
3. **From catalog** — Search GeoNode's datasets by title or keyword and click to add.
4. **From external service** — Enter a WMS/WMTS URL to add layers from external servers.
5. The layer appears in the layer list and on the map.

### 5.4 Layer Controls

In the **Layers** panel:

- **Visibility** — Click the eye icon to show/hide a layer.
- **Opacity** — Drag the opacity slider (0% transparent to 100% opaque).
- **Ordering** — Drag layers up/down to change their stacking order. Layers at the top of the list render on top of the map.
- **Zoom to layer** — Right-click a layer and select **Zoom to Extent**.
- **Remove** — Click the trash icon to remove a layer from the map.

### 5.5 Styling Layers

Within MapStore, you can adjust layer styling:

1. Right-click a layer in the layer panel and select **Style**.
2. Choose from available SLD styles in the dropdown.
3. For basic changes, use the visual style editor to adjust colors, sizes, and labels.
4. Click **Apply** to preview changes, then **Save** to persist.

### 5.6 Saving and Sharing

- **Save** — Click the **Save** button (disk icon) to save the map with its current layers, extent, and styles.
- **Save As** — Create a copy under a new name.
- **Permalink** — Share a link that reproduces the exact map state (center, zoom, visible layers).
- **Embed** — Copy an `<iframe>` snippet to embed the map in another website.

### 5.7 Map Metadata

Maps have the same metadata fields as datasets. After saving, edit metadata from the map detail page following the same steps described in section 4.4.

---

## 6. Documents

Documents are non-spatial files stored in GeoNode's catalog — reports, PDFs, images, spreadsheets, or any other file type.

### 6.1 Uploading a Document

1. Click **Documents** in the navigation menu.
2. Click **Upload Document** (top-right).
3. Drag and drop or browse to select your file.
   - Alternatively, provide an **external URL** to reference a remote document without uploading.
4. Fill in the title and click **Upload**.

### 6.2 Linking Documents to Resources

Documents can be linked to datasets, maps, or other resources to provide context:

1. On the document detail page, click **Edit** → **Linked Resources**.
2. Search for and select the resources to associate with.
3. Click **Save**.

Linked documents appear on the related resource's detail page under **Linked Resources**.

### 6.3 Document Metadata

Documents use the same metadata schema as other resources. At minimum, fill in **Title**, **Abstract**, **Category**, and **Keywords**.

### 6.4 Viewing and Downloading

- **Preview** — PDFs and images can be previewed directly in the browser.
- **Download** — Click **Download** to save the original file.

---

## 7. GeoApps

GeoApps are custom web applications or dashboards built on GeoNode data. They extend GeoNode beyond simple maps.

### 7.1 What Are GeoApps

GeoApps let you create interactive experiences — dashboards with charts and maps, story maps, or custom visualization tools. The available application types depend on your GeoNode installation's configuration.

### 7.2 Creating a GeoApp

1. Click **GeoApps** in the navigation menu.
2. Click **Create GeoApp** (top-right).
3. Choose an application type/template (if multiple are available).
4. Give it a **name** and click **Create**.
5. The application editor opens for configuration.

### 7.3 Configuring a GeoApp

The configuration interface varies by app type. Common capabilities include:

- Adding **map widgets** that display GeoNode datasets.
- Adding **charts** (bar, line, pie) driven by dataset attributes.
- Adding **text panels** for narrative content.
- Arranging widgets in a responsive layout.

### 7.4 Publishing and Sharing

Once configured, save the GeoApp. It appears in the GeoApps listing and can be:

- Shared via permalink.
- Embedded in external websites with an `<iframe>`.
- Restricted with the same permissions model as other resources.

---

## 8. Permissions and Sharing

GeoNode provides granular, resource-level access control.

### 8.1 Permission Model

Each resource can have these permission levels assigned to users or groups:

| Permission | What It Allows |
|------------|----------------|
| **View Metadata** | See the resource in listings and read its metadata |
| **View Resource** | See the actual data — map preview, attribute table |
| **Download** | Download the resource in available formats |
| **Edit** | Modify metadata, replace data, manage styles |
| **Manage** | Change permissions, delete the resource |

Permissions are additive — a user with **Download** also has **View Resource** and **View Metadata**.

### 8.2 Setting Permissions on a Resource

1. On any resource detail page, click the **Share** button (or lock icon).
2. The permissions dialog shows current access settings.
3. To add a user: type a username in the search field, select the user, and choose their permission level.
4. To add a group: switch to the **Groups** tab, search for and select a group, and set permissions.
5. Click **Save** to apply.

### 8.3 Public vs. Private Resources

- **Public** — Visible and accessible to anyone, including anonymous (not logged in) users. Set by granting **View** permission to "Anyone" or "Anonymous".
- **Private** — Only visible to explicitly listed users and groups. The default for new uploads in many GeoNode configurations.

> **Tip:** Check your organization's default permission policy. Administrators can configure whether new resources are public or private by default.

### 8.4 Group-Based Permissions

For managing access at scale, use groups instead of individual users:

1. Create a group (see section 10.4) for a team or project.
2. Add members to the group.
3. Assign permissions to the group on each resource.

When group membership changes, permissions update automatically for all the group's resources.

### 8.5 Publish Permission

The **Publish** permission controls who can change a resource's publication state (draft → published). Only users with this permission (typically editors, managers, or administrators) can make resources publicly discoverable.

---

## 9. Publication Workflow

GeoNode supports a multi-stage publication workflow to ensure data quality and approval before public access.

### 9.1 Resource States

| State | Meaning |
|-------|---------|
| **Draft** | Uploaded but not yet submitted for review. Visible only to the owner and explicitly permitted users. |
| **Pending Approval** | Submitted for review by a manager or administrator. |
| **Approved** | Reviewed and approved. May or may not be publicly visible depending on permissions. |
| **Published** | Visible in public listings and search results. |
| **Featured** | Highlighted on the home page carousel or featured section. |

### 9.2 Submitting for Approval

1. After uploading and completing metadata, open the resource detail page.
2. If your organization uses approval workflows, click **Submit for Approval** (or toggle the **Approved** switch if you have permission).
3. The resource moves to "Pending Approval" status.

### 9.3 Approving and Publishing

Administrators or designated reviewers:

1. Navigate to the resource detail page.
2. Review the metadata, data quality, and permissions.
3. Toggle **Approved** to approve the resource.
4. Toggle **Published** to make it visible in public listings.

### 9.4 Featuring a Resource

To highlight a resource on the home page:

1. Open the resource detail page (requires admin permissions).
2. Toggle **Featured** to on.
3. The resource appears in the featured carousel or section on the GeoNode home page.

> **Tip:** Feature resources that are high-quality, timely, and broadly relevant to your organization's audience.

---

## 10. Users and Groups

### 10.1 People Page

Click **People** in the navigation menu to browse all registered users. Each profile card shows the user's name, organization, and resource count.

### 10.2 User Roles

| Role | Capabilities |
|------|-------------|
| **Anonymous** | View public resources, search the catalog |
| **Registered User** | Upload datasets/documents, create maps, manage own resources |
| **Editor** | Extended permissions to publish resources |
| **Group Manager** | Manage group membership and group resources |
| **Administrator** | Full access — manage users, groups, harvesters, settings, all resources |

Roles may vary depending on your organization's GeoNode configuration.

### 10.3 Groups

Click **Groups** in the navigation menu to see all groups. Each group has:

- **Members** — Users who belong to the group.
- **Managers** — Users who can manage the group.
- **Resources** — Datasets, maps, and documents assigned to the group.
- **Description** and **logo**.

To join a group (if open membership is enabled), click **Join** on the group page.

### 10.4 Managing Groups (Admin/Manager)

1. Click **Groups** → **Create Group** (admin only).
2. Fill in **Name**, **Description**, and optionally upload a **Logo**.
3. Set the group's membership policy: **Open** (anyone can join), **Closed** (invitation only), or **By Approval** (request + approval).
4. Add members by searching usernames and assigning roles (member or manager).
5. Click **Save**.

To manage an existing group, open the group page and click **Edit**.

### 10.5 Transferring Resource Ownership

Administrators can reassign resource ownership:

1. Open the resource detail page.
2. Click **Edit** → **Change Owner**.
3. Search for and select the new owner.
4. Click **Save**.

The new owner gains full control of the resource.

---

## 11. Harvesting (Admin)

Harvesting allows GeoNode to automatically import metadata and resources from remote OGC-compliant services.

### 11.1 What Is Harvesting

Instead of manually uploading data, harvesting connects to a remote service, discovers its available resources, and imports them into GeoNode's catalog. The imported resources are proxied through GeoNode, providing unified search, metadata management, and permissions.

### 11.2 Supported Remote Sources

| Source Type | What It Harvests |
|-------------|-----------------|
| **Other GeoNode instances** | Datasets, maps, documents from a remote GeoNode |
| **OGC WMS** | Layers from any WMS-compliant service |
| **OGC WFS** | Feature types from WFS services |
| **OGC CSW** | Metadata records from CSW catalogs |
| **ArcGIS REST** | Layers from ArcGIS Server REST API |

### 11.3 Configuring a Harvester

1. Navigate to the **Admin** panel (admin users only).
2. Go to **Harvesting** → **Add Harvester**.
3. Configure:
   - **Name** — Descriptive name for this harvester (e.g. "Regional WMS Service").
   - **Remote URL** — Base URL of the remote service.
   - **Harvester Type** — Select the appropriate type for the remote service.
   - **Scheduling** — Enable automatic periodic harvesting.
   - **Frequency** — How often to check for new/updated resources (in minutes).
   - **Default Owner** — Which GeoNode user will own harvested resources.
   - **Auto-harvest new resources** — Automatically import newly discovered resources.
   - **Delete orphans** — Remove local resources that no longer exist on the remote service.
4. Click **Save**.

### 11.4 Running and Monitoring

- **Manual harvest** — Click **Run Harvest** to trigger an immediate harvest session.
- **Status** — View the harvest session log showing discovered, imported, updated, and failed resources.
- **Harvestable resources** — Browse all resources found on the remote service and select which ones to import.

> **Tip:** Start with automatic harvesting disabled. Run a manual harvest first to review what will be imported, then enable scheduling once you're confident in the configuration.

---

## 12. Tips and Best Practices

### Metadata Quality

- Always fill in **Title**, **Abstract**, **Category**, **Keywords**, and **License** at minimum.
- Use descriptive titles that include the geographic area and time period — "Temperature Readings — South Tyrol 2020-2024" is better than "temp_data_v3".
- Choose keywords from your organization's controlled vocabulary when available.
- Fill in the **Temporal Extent** so users can find data by time period.

### File Preparation

- **Coordinate Reference System** — Use EPSG:4326 (WGS 84) or EPSG:3857 (Web Mercator) for web maps. If your data is in a local CRS, ensure a valid .prj file is included.
- **Shapefiles** — Zip all component files (.shp, .shx, .dbf, .prj, and optionally .cpg for encoding) into a single .zip. Do not nest the files inside a subfolder within the zip.
- **GeoTIFF optimization** — Use internal tiling and overviews (pyramids) for large rasters. This dramatically improves rendering performance. Tools: `gdaladdo` and `gdal_translate -co TILED=YES`.
- **GeoJSON** — Keep files under 50 MB. For larger datasets, use GeoPackage instead.

### Permissions Strategy

- Start with **private by default** and grant access intentionally.
- Use **groups** rather than individual user permissions whenever possible.
- Review permissions before publishing — once a resource is public, anyone can access it.
- Assign the **minimum necessary permission** (e.g. give "View" not "Download" if download isn't needed).

### Naming Conventions

- Use consistent, descriptive names for datasets and maps.
- Include geographic scope and date/version in titles where relevant.
- Avoid internal codes or abbreviations that external users won't understand.

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| **Dataset** | A geospatial data file published in GeoNode — vector (points, lines, polygons) or raster (gridded imagery/elevation). Also called a "layer". |
| **Map** | An interactive web map composed of one or more datasets as layers, with configured styles and extent. |
| **Document** | A non-spatial file (PDF, image, report) stored in GeoNode's catalog. |
| **GeoApp** | A custom web application or dashboard built on GeoNode data. |
| **Resource** | Generic term for any content in GeoNode — datasets, maps, documents, and geoapps. |
| **Metadata** | Descriptive information about a resource — title, abstract, keywords, dates, contacts, spatial extent, license. |
| **SLD** | Styled Layer Descriptor — an XML format for defining how geospatial data is styled on a map. |
| **OGC** | Open Geospatial Consortium — the standards body that defines WMS, WFS, WCS, and other geospatial protocols. |
| **WMS** | Web Map Service — an OGC standard for serving map images over HTTP. |
| **WFS** | Web Feature Service — an OGC standard for serving vector features (with attributes) over HTTP. |
| **WCS** | Web Coverage Service — an OGC standard for serving raster data over HTTP. |
| **CSW** | Catalog Service for the Web — an OGC standard for searching and retrieving metadata records. |
| **EPSG** | European Petroleum Survey Group — maintains a registry of coordinate reference systems. EPSG:4326 = WGS 84 (latitude/longitude). |
| **Shapefile** | A common vector data format consisting of multiple component files (.shp, .shx, .dbf, .prj). Must be zipped for upload. |
| **GeoTIFF** | A raster image format with embedded geospatial metadata (CRS, extent). |
| **GeoJSON** | A JSON-based format for encoding geographic data structures. |
| **GeoPackage** | An SQLite-based open format for storing vector and raster geospatial data. |
| **MapStore** | The open-source map viewer framework used by GeoNode for creating and displaying interactive maps. |
| **Thesaurus** | A controlled vocabulary of standardized terms (e.g. INSPIRE themes) used for consistent keyword tagging. |
| **Harvester** | A GeoNode component that automatically imports resources from remote OGC services. |
| **CRS** | Coordinate Reference System — defines how geographic coordinates map to locations on Earth. |

---

## 14. Further Resources

- **GeoNode Documentation** — [https://docs.geonode.org](https://docs.geonode.org) — Official installation, administration, and development docs.
- **MapStore Documentation** — [https://mapstore.readthedocs.io](https://mapstore.readthedocs.io) — Map viewer and editor documentation.
- **GeoNode API / CLI Documentation** — See [README.md](README.md) in this repository for the REST API reference and CLI tool usage.
- **GeoNode Community** — [https://github.com/GeoNode/geonode](https://github.com/GeoNode/geonode) — Source code, issues, and discussions.
