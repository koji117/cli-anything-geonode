"""GeoNode CLI — command-line interface for GeoNode geospatial CMS."""

import json as json_mod
import os
import shlex

import click

from cli_anything.geonode.core.client import GeoNodeClient, GeoNodeError
from cli_anything.geonode.core.config import (
    load_config, save_config, set_url, set_token, set_credentials,
    show_config, clear_config,
)
from cli_anything.geonode.core.session import Session
from cli_anything.geonode.utils.formatters import (
    format_dataset_list, format_map_list, format_document_list,
    format_resource_list, format_resource_detail, format_user_list,
    format_group_list, format_permissions, format_upload_list,
    format_config, format_geoapp_list, format_harvester_list,
    format_execution_list, format_facet_list, format_category_list,
    format_region_list, format_keyword_list,
)


# ── Helpers ──────────────────────────────────────────────────────────────

def _output(ctx, data, human_fn=None):
    """Output data as JSON or human-readable."""
    if ctx.obj.get("json_mode"):
        click.echo(json_mod.dumps(data, indent=2, default=str))
    elif human_fn:
        human_fn(data)
    else:
        click.echo(json_mod.dumps(data, indent=2, default=str))


def _get_client(ctx):
    """Get GeoNodeClient from context."""
    return ctx.obj["client"]


def _handle_error(ctx, e):
    """Handle GeoNodeError."""
    if ctx.obj.get("json_mode"):
        click.echo(json_mod.dumps({
            "error": str(e),
            "status_code": getattr(e, "status_code", None),
        }), err=True)
    else:
        click.echo(f"Error: {e}", err=True)
        if hasattr(e, "response_text") and e.response_text:
            click.echo(f"  Response: {e.response_text[:200]}", err=True)
    ctx.exit(1)


# ── Main CLI Group ───────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--url", envvar="GEONODE_URL", default=None,
              help="GeoNode instance URL")
@click.option("--token", envvar="GEONODE_TOKEN", default=None,
              help="API key / OAuth token")
@click.option("--user", envvar="GEONODE_USER", default=None, help="Username")
@click.option("--password", envvar="GEONODE_PASSWORD", default=None, help="Password")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.option("--page-size", type=int, default=10, help="Results per page")
@click.version_option(version="1.0.0", prog_name="cli-anything-geonode")
@click.pass_context
def cli(ctx, url, token, user, password, json_mode, page_size):
    """CLI harness for GeoNode geospatial content management system.

    Manages datasets, maps, documents, users, and groups via
    GeoNode's REST API v2.
    """
    ctx.ensure_object(dict)

    # Load saved config as defaults
    config = load_config()
    url = url or config.get("url", "http://localhost:8000")
    token = token or config.get("token")
    user = user or config.get("username")
    password = password or config.get("password")

    ctx.obj["client"] = GeoNodeClient(url=url, token=token,
                                       username=user, password=password)
    ctx.obj["json_mode"] = json_mode
    ctx.obj["page_size"] = page_size
    ctx.obj["session"] = Session(url=url, auth_type="token" if token else "basic",
                                  token=token, username=user, password=password)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── REPL ─────────────────────────────────────────────────────────────────

@cli.command(hidden=True)
@click.pass_context
def repl(ctx):
    """Interactive REPL mode."""
    from cli_anything.geonode.utils.repl_skin import ReplSkin

    skin = ReplSkin("geonode", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands_help = {
        "config show/test/set-url/set-token": "Connection configuration",
        "dataset list/info/upload/update/delete": "Dataset management",
        "dataset metadata/permissions/maps": "Dataset metadata & relations",
        "map list/info/create/update/delete": "Map management",
        "map layers/datasets": "Map layer & dataset relations",
        "document list/info/upload/update/delete": "Document management",
        "geoapp list/info/create/update/delete": "GeoApp management",
        "resource list/search/info/copy/delete": "Unified resource operations",
        "resource favorites/approved/published": "Filtered resource lists",
        "resource favorite/permissions/types": "Resource actions",
        "resource set-thumbnail/extra-metadata": "Resource metadata",
        "resource linked-resources/upload-asset": "Resource relations & assets",
        "user list/info/create/update/delete/me": "User management",
        "group list/info/members/managers": "Group management",
        "upload list/status/imports": "Upload monitoring",
        "execution list/info/status/delete": "Async execution requests",
        "harvester list/info/create/update": "Harvester management",
        "metadata info/schema/instance": "Metadata management",
        "metadata autocomplete <entity>": "Metadata autocomplete",
        "facet list / facet get <name>": "Faceted search",
        "category list/info": "Topic categories",
        "region list/info": "Geographic regions",
        "keyword list/info/thesaurus": "Keywords & thesaurus",
        "owner list/info": "Resource owners",
        "schema": "OpenAPI schema",
        "status": "Show session status",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, project_name="", modified=False)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue

        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if line == "help":
            skin.help(commands_help)
            continue

        if line == "status":
            info = ctx.obj["session"].status()
            for k, v in info.items():
                skin.status(k, str(v))
            continue

        # Dispatch to Click commands
        try:
            args = shlex.split(line)
            cli.main(args=args, ctx=ctx, standalone_mode=False)
        except SystemExit:
            pass
        except GeoNodeError as e:
            skin.error(str(e))
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(f"Unexpected error: {e}")


# ── Config Commands ──────────────────────────────────────────────────────

@cli.group("config")
@click.pass_context
def config_group(ctx):
    """Connection configuration commands."""
    pass


@config_group.command("show")
@click.pass_context
def config_show(ctx):
    """Show current connection configuration."""
    data = show_config()
    _output(ctx, data, format_config)


@config_group.command("set-url")
@click.argument("url")
@click.pass_context
def config_set_url(ctx, url):
    """Set the GeoNode instance URL."""
    data = set_url(url)
    _output(ctx, data, lambda d: click.echo(f"URL set to: {d['url']}"))


@config_group.command("set-token")
@click.argument("token")
@click.pass_context
def config_set_token(ctx, token):
    """Set the API key / OAuth token."""
    data = set_token(token)
    _output(ctx, data, lambda d: click.echo("Token saved."))


@config_group.command("set-credentials")
@click.argument("username")
@click.argument("password")
@click.pass_context
def config_set_creds(ctx, username, password):
    """Set Basic Auth credentials."""
    data = set_credentials(username, password)
    _output(ctx, data, lambda d: click.echo(f"Credentials set for: {d['username']}"))


@config_group.command("test")
@click.pass_context
def config_test(ctx):
    """Test connection to GeoNode."""
    try:
        client = _get_client(ctx)
        result = client.test_connection()
        _output(ctx, {"status": "ok", "url": client.base_url, "response": result},
                lambda d: click.echo(f"Connected to GeoNode at {d['url']}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@config_group.command("clear")
@click.pass_context
def config_clear(ctx):
    """Reset configuration to defaults."""
    data = clear_config()
    _output(ctx, data, lambda d: click.echo("Configuration reset to defaults."))


# ── Dataset Commands ─────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def dataset(ctx):
    """Dataset (layer) management commands."""
    pass


@dataset.command("list")
@click.option("--owner", default=None, help="Filter by owner username")
@click.option("--category", default=None, help="Filter by category")
@click.option("--keyword", default=None, help="Filter by keyword")
@click.option("--search", "query", default=None, help="Full-text search")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def dataset_list(ctx, owner, category, keyword, query, page):
    """List datasets."""
    try:
        client = _get_client(ctx)
        filters = {}
        if owner:
            filters["filter{owner.username}"] = owner
        if category:
            filters["filter{category.identifier}"] = category
        if keyword:
            filters["filter{keywords.slug__in}"] = keyword
        if query:
            filters["search"] = query
        data = client.list_datasets(page=page,
                                     page_size=ctx.obj["page_size"], **filters)
        _output(ctx, data, format_dataset_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("info")
@click.argument("pk", type=int)
@click.pass_context
def dataset_info(ctx, pk):
    """Show dataset details."""
    try:
        client = _get_client(ctx)
        data = client.get_dataset(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("upload")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--title", default=None, help="Dataset title")
@click.option("--abstract", default=None, help="Dataset description")
@click.option("--category", default=None, help="Category identifier")
@click.option("--keyword", multiple=True, help="Keywords (repeatable)")
@click.pass_context
def dataset_upload(ctx, file_path, title, abstract, category, keyword):
    """Upload a geospatial dataset file."""
    try:
        client = _get_client(ctx)
        keywords = list(keyword) if keyword else None
        data = client.upload_dataset(file_path, title=title, abstract=abstract,
                                      category=category, keywords=keywords)
        _output(ctx, data, lambda d: click.echo(
            f"Upload started: {json_mod.dumps(d, indent=2, default=str)}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("update")
@click.argument("pk", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--abstract", default=None, help="New description")
@click.pass_context
def dataset_update(ctx, pk, title, abstract):
    """Update dataset metadata."""
    try:
        client = _get_client(ctx)
        updates = {}
        if title:
            updates["title"] = title
        if abstract:
            updates["abstract"] = abstract
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        data = client.update_dataset(pk, **updates)
        _output(ctx, data, lambda d: click.echo(f"Dataset {pk} updated."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("delete")
@click.argument("pk", type=int)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@click.pass_context
def dataset_delete(ctx, pk, confirm):
    """Delete a dataset."""
    if not confirm and not ctx.obj.get("json_mode"):
        click.confirm(f"Delete dataset {pk}?", abort=True)
    try:
        client = _get_client(ctx)
        data = client.delete_dataset(pk)
        _output(ctx, data, lambda d: click.echo(f"Dataset {pk} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("permissions")
@click.argument("pk", type=int)
@click.option("--set-json", default=None, help="Set permissions from JSON string")
@click.pass_context
def dataset_permissions(ctx, pk, set_json):
    """View or set dataset permissions."""
    try:
        client = _get_client(ctx)
        if set_json:
            perms = json_mod.loads(set_json)
            data = client.set_dataset_permissions(pk, perms)
            _output(ctx, data, lambda d: click.echo(f"Permissions updated for dataset {pk}."))
        else:
            data = client.get_dataset_permissions(pk)
            _output(ctx, data, format_permissions)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("metadata")
@click.argument("pk", type=int)
@click.argument("xml_file", type=click.Path(exists=True))
@click.pass_context
def dataset_metadata(ctx, pk, xml_file):
    """Upload ISO metadata XML for a dataset."""
    try:
        client = _get_client(ctx)
        data = client.upload_dataset_metadata(pk, xml_file)
        _output(ctx, data, lambda d: click.echo(f"Metadata uploaded for dataset {pk}."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("maplayers")
@click.argument("pk", type=int)
@click.pass_context
def dataset_maplayers(ctx, pk):
    """Show map layers that use this dataset."""
    try:
        client = _get_client(ctx)
        data = client.get_dataset_maplayers(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@dataset.command("maps")
@click.argument("pk", type=int)
@click.pass_context
def dataset_maps(ctx, pk):
    """Show maps that use this dataset."""
    try:
        client = _get_client(ctx)
        data = client.get_dataset_maps(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Map Commands ─────────────────────────────────────────────────────────

@cli.group("map")
@click.pass_context
def map_group(ctx):
    """Map management commands."""
    pass


@map_group.command("list")
@click.option("--search", "query", default=None, help="Full-text search")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def map_list(ctx, query, page):
    """List maps."""
    try:
        client = _get_client(ctx)
        filters = {}
        if query:
            filters["search"] = query
        data = client.list_maps(page=page,
                                 page_size=ctx.obj["page_size"], **filters)
        _output(ctx, data, format_map_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@map_group.command("info")
@click.argument("pk", type=int)
@click.pass_context
def map_info(ctx, pk):
    """Show map details."""
    try:
        client = _get_client(ctx)
        data = client.get_map(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@map_group.command("create")
@click.option("--title", required=True, help="Map title")
@click.option("--abstract", default=None, help="Map description")
@click.pass_context
def map_create(ctx, title, abstract):
    """Create a new map."""
    try:
        client = _get_client(ctx)
        payload = {"title": title}
        if abstract:
            payload["abstract"] = abstract
        data = client.create_map(**payload)
        _output(ctx, data, lambda d: click.echo(
            f"Map created: {d.get('pk', d.get('id', 'unknown'))}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@map_group.command("update")
@click.argument("pk", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--abstract", default=None, help="New description")
@click.pass_context
def map_update(ctx, pk, title, abstract):
    """Update a map."""
    try:
        client = _get_client(ctx)
        updates = {}
        if title:
            updates["title"] = title
        if abstract:
            updates["abstract"] = abstract
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        data = client.update_map(pk, **updates)
        _output(ctx, data, lambda d: click.echo(f"Map {pk} updated."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@map_group.command("delete")
@click.argument("pk", type=int)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@click.pass_context
def map_delete(ctx, pk, confirm):
    """Delete a map."""
    if not confirm and not ctx.obj.get("json_mode"):
        click.confirm(f"Delete map {pk}?", abort=True)
    try:
        client = _get_client(ctx)
        data = client.delete_map(pk)
        _output(ctx, data, lambda d: click.echo(f"Map {pk} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@map_group.command("layers")
@click.argument("pk", type=int)
@click.pass_context
def map_layers(ctx, pk):
    """List layers in a map."""
    try:
        client = _get_client(ctx)
        data = client.get_map_layers(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@map_group.command("datasets")
@click.argument("pk", type=int)
@click.pass_context
def map_datasets(ctx, pk):
    """List datasets used in a map."""
    try:
        client = _get_client(ctx)
        data = client.get_map_datasets(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Document Commands ────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def document(ctx):
    """Document management commands."""
    pass


@document.command("list")
@click.option("--search", "query", default=None, help="Full-text search")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def document_list(ctx, query, page):
    """List documents."""
    try:
        client = _get_client(ctx)
        filters = {}
        if query:
            filters["search"] = query
        data = client.list_documents(page=page,
                                      page_size=ctx.obj["page_size"], **filters)
        _output(ctx, data, format_document_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@document.command("info")
@click.argument("pk", type=int)
@click.pass_context
def document_info(ctx, pk):
    """Show document details."""
    try:
        client = _get_client(ctx)
        data = client.get_document(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@document.command("upload")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--title", default=None, help="Document title")
@click.option("--abstract", default=None, help="Document description")
@click.pass_context
def document_upload(ctx, file_path, title, abstract):
    """Upload a document."""
    try:
        client = _get_client(ctx)
        data = client.upload_document(file_path, title=title, abstract=abstract)
        _output(ctx, data, lambda d: click.echo(
            f"Document uploaded: {d.get('pk', d.get('id', 'unknown'))}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@document.command("update")
@click.argument("pk", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--abstract", default=None, help="New description")
@click.pass_context
def document_update(ctx, pk, title, abstract):
    """Update document metadata."""
    try:
        client = _get_client(ctx)
        updates = {}
        if title:
            updates["title"] = title
        if abstract:
            updates["abstract"] = abstract
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        data = client.update_document(pk, **updates)
        _output(ctx, data, lambda d: click.echo(f"Document {pk} updated."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@document.command("delete")
@click.argument("pk", type=int)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@click.pass_context
def document_delete(ctx, pk, confirm):
    """Delete a document."""
    if not confirm and not ctx.obj.get("json_mode"):
        click.confirm(f"Delete document {pk}?", abort=True)
    try:
        client = _get_client(ctx)
        data = client.delete_document(pk)
        _output(ctx, data, lambda d: click.echo(f"Document {pk} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@document.command("linked-resources")
@click.argument("pk", type=int)
@click.pass_context
def document_linked(ctx, pk):
    """Show resources linked to a document."""
    try:
        client = _get_client(ctx)
        data = client.get_document_linked_resources(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Resource Commands ────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def resource(ctx):
    """Generic resource operations."""
    pass


@resource.command("list")
@click.option("--type", "resource_type", default=None,
              help="Filter by type (dataset, map, document)")
@click.option("--search", "query", default=None, help="Full-text search")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def resource_list(ctx, resource_type, query, page):
    """List all resources."""
    try:
        client = _get_client(ctx)
        filters = {}
        if resource_type:
            filters["filter{resource_type__in}"] = resource_type
        if query:
            filters["search"] = query
        data = client.list_resources(page=page,
                                      page_size=ctx.obj["page_size"], **filters)
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("search")
@click.argument("query")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def resource_search(ctx, query, page):
    """Search resources by text query."""
    try:
        client = _get_client(ctx)
        data = client.search_resources(query, page=page,
                                        page_size=ctx.obj["page_size"])
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("info")
@click.argument("pk", type=int)
@click.pass_context
def resource_info(ctx, pk):
    """Show resource details."""
    try:
        client = _get_client(ctx)
        data = client.get_resource(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("permissions")
@click.argument("pk", type=int)
@click.option("--set-json", default=None, help="Set permissions from JSON string")
@click.pass_context
def resource_permissions(ctx, pk, set_json):
    """View or set resource permissions."""
    try:
        client = _get_client(ctx)
        if set_json:
            perms = json_mod.loads(set_json)
            data = client.set_resource_permissions(pk, perms)
            _output(ctx, data, lambda d: click.echo(f"Permissions updated for resource {pk}."))
        else:
            data = client.get_resource_permissions(pk)
            _output(ctx, data, format_permissions)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("copy")
@click.argument("pk", type=int)
@click.pass_context
def resource_copy(ctx, pk):
    """Copy a resource."""
    try:
        client = _get_client(ctx)
        data = client.copy_resource(pk)
        _output(ctx, data, lambda d: click.echo(
            f"Resource {pk} copied: {d.get('pk', d.get('id', 'unknown'))}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("delete")
@click.argument("pk", type=int)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@click.pass_context
def resource_delete(ctx, pk, confirm):
    """Delete a resource."""
    if not confirm and not ctx.obj.get("json_mode"):
        click.confirm(f"Delete resource {pk}?", abort=True)
    try:
        client = _get_client(ctx)
        data = client.delete_resource(pk)
        _output(ctx, data, lambda d: click.echo(f"Resource {pk} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("approved")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def resource_approved(ctx, page):
    """List approved resources."""
    try:
        client = _get_client(ctx)
        data = client.list_approved_resources(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("published")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def resource_published(ctx, page):
    """List published resources."""
    try:
        client = _get_client(ctx)
        data = client.list_published_resources(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("featured")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def resource_featured(ctx, page):
    """List featured resources."""
    try:
        client = _get_client(ctx)
        data = client.list_featured_resources(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("favorites")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def resource_favorites(ctx, page):
    """List your favorite resources."""
    try:
        client = _get_client(ctx)
        data = client.list_favorite_resources(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("favorite")
@click.argument("pk", type=int)
@click.option("--remove", is_flag=True, help="Remove from favorites")
@click.pass_context
def resource_favorite(ctx, pk, remove):
    """Add or remove a resource from favorites."""
    try:
        client = _get_client(ctx)
        if remove:
            data = client.remove_favorite(pk)
            _output(ctx, data, lambda d: click.echo(f"Resource {pk} removed from favorites."))
        else:
            data = client.add_favorite(pk)
            _output(ctx, data, lambda d: click.echo(f"Resource {pk} added to favorites."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("types")
@click.pass_context
def resource_types(ctx):
    """List available resource types with counts."""
    try:
        client = _get_client(ctx)
        data = client.get_resource_types()
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("set-thumbnail")
@click.argument("pk", type=int)
@click.option("--file", "file_path", type=click.Path(exists=True), help="Thumbnail image file")
@click.option("--url", "thumb_url", default=None, help="Thumbnail URL")
@click.pass_context
def resource_set_thumbnail(ctx, pk, file_path, thumb_url):
    """Set resource thumbnail from file or URL."""
    try:
        client = _get_client(ctx)
        data = client.set_thumbnail(pk, file_path=file_path, url=thumb_url)
        _output(ctx, data, lambda d: click.echo(f"Thumbnail set for resource {pk}."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("extra-metadata")
@click.argument("pk", type=int)
@click.option("--set-json", default=None, help="Set extra metadata from JSON")
@click.option("--delete", "do_delete", is_flag=True, help="Delete extra metadata")
@click.pass_context
def resource_extra_metadata(ctx, pk, set_json, do_delete):
    """View, set, or delete extra metadata."""
    try:
        client = _get_client(ctx)
        if do_delete:
            data = client.delete_extra_metadata(pk)
            _output(ctx, data, lambda d: click.echo(f"Extra metadata deleted for resource {pk}."))
        elif set_json:
            metadata = json_mod.loads(set_json)
            data = client.update_extra_metadata(pk, metadata)
            _output(ctx, data, lambda d: click.echo(f"Extra metadata updated for resource {pk}."))
        else:
            data = client.get_extra_metadata(pk)
            _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("iso-metadata")
@click.argument("pk", type=int)
@click.pass_context
def resource_iso_metadata(ctx, pk):
    """Get ISO metadata XML for a resource."""
    try:
        client = _get_client(ctx)
        data = client.get_iso_metadata_xml(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("linked-resources")
@click.argument("pk", type=int)
@click.option("--add", "add_pks", default=None, help="Add linked resources (comma-separated PKs)")
@click.option("--remove", "remove_pks", default=None, help="Remove linked resources (comma-separated PKs)")
@click.pass_context
def resource_linked(ctx, pk, add_pks, remove_pks):
    """View, add, or remove linked resources."""
    try:
        client = _get_client(ctx)
        if add_pks:
            pks = [int(x.strip()) for x in add_pks.split(",")]
            data = client.add_linked_resources(pk, pks)
            _output(ctx, data, lambda d: click.echo(f"Linked resources added to {pk}."))
        elif remove_pks:
            pks = [int(x.strip()) for x in remove_pks.split(",")]
            data = client.remove_linked_resources(pk, pks)
            _output(ctx, data, lambda d: click.echo(f"Linked resources removed from {pk}."))
        else:
            data = client.get_linked_resources(pk)
            _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("upload-asset")
@click.argument("pk", type=int)
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def resource_upload_asset(ctx, pk, file_path):
    """Upload an asset for a resource."""
    try:
        client = _get_client(ctx)
        data = client.upload_asset(pk, file_path)
        _output(ctx, data, lambda d: click.echo(
            f"Asset uploaded for resource {pk}."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@resource.command("delete-asset")
@click.argument("pk", type=int)
@click.argument("asset_id", type=int)
@click.pass_context
def resource_delete_asset(ctx, pk, asset_id):
    """Delete an asset from a resource."""
    try:
        client = _get_client(ctx)
        data = client.delete_asset(pk, asset_id)
        _output(ctx, data, lambda d: click.echo(f"Asset {asset_id} deleted from resource {pk}."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── GeoApp Commands ──────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def geoapp(ctx):
    """GeoApp management commands."""
    pass


@geoapp.command("list")
@click.option("--search", "query", default=None, help="Full-text search")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def geoapp_list(ctx, query, page):
    """List geoapps."""
    try:
        client = _get_client(ctx)
        filters = {}
        if query:
            filters["search"] = query
        data = client.list_geoapps(page=page,
                                    page_size=ctx.obj["page_size"], **filters)
        _output(ctx, data, format_geoapp_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@geoapp.command("info")
@click.argument("pk", type=int)
@click.pass_context
def geoapp_info(ctx, pk):
    """Show geoapp details."""
    try:
        client = _get_client(ctx)
        data = client.get_geoapp(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@geoapp.command("create")
@click.option("--title", required=True, help="GeoApp title")
@click.option("--abstract", default=None, help="GeoApp description")
@click.pass_context
def geoapp_create(ctx, title, abstract):
    """Create a new geoapp."""
    try:
        client = _get_client(ctx)
        payload = {"title": title}
        if abstract:
            payload["abstract"] = abstract
        data = client.create_geoapp(**payload)
        _output(ctx, data, lambda d: click.echo(
            f"GeoApp created: {d.get('pk', d.get('id', 'unknown'))}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@geoapp.command("update")
@click.argument("pk", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--abstract", default=None, help="New description")
@click.pass_context
def geoapp_update(ctx, pk, title, abstract):
    """Update a geoapp."""
    try:
        client = _get_client(ctx)
        updates = {}
        if title:
            updates["title"] = title
        if abstract:
            updates["abstract"] = abstract
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        data = client.update_geoapp(pk, **updates)
        _output(ctx, data, lambda d: click.echo(f"GeoApp {pk} updated."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@geoapp.command("delete")
@click.argument("pk", type=int)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@click.pass_context
def geoapp_delete(ctx, pk, confirm):
    """Delete a geoapp."""
    if not confirm and not ctx.obj.get("json_mode"):
        click.confirm(f"Delete geoapp {pk}?", abort=True)
    try:
        client = _get_client(ctx)
        data = client.delete_geoapp(pk)
        _output(ctx, data, lambda d: click.echo(f"GeoApp {pk} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── User Commands ────────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def user(ctx):
    """User management commands."""
    pass


@user.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def user_list(ctx, page):
    """List users."""
    try:
        client = _get_client(ctx)
        data = client.list_users(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_user_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@user.command("info")
@click.argument("pk", type=int)
@click.pass_context
def user_info(ctx, pk):
    """Show user details."""
    try:
        client = _get_client(ctx)
        data = client.get_user(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@user.command("create")
@click.argument("username")
@click.argument("password")
@click.option("--email", default=None, help="Email address")
@click.option("--first-name", default=None, help="First name")
@click.option("--last-name", default=None, help="Last name")
@click.pass_context
def user_create(ctx, username, password, email, first_name, last_name):
    """Create a new user."""
    try:
        client = _get_client(ctx)
        extra = {}
        if first_name:
            extra["first_name"] = first_name
        if last_name:
            extra["last_name"] = last_name
        data = client.create_user(username, password, email=email, **extra)
        _output(ctx, data, lambda d: click.echo(f"User '{username}' created."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@user.command("update")
@click.argument("pk", type=int)
@click.option("--first-name", default=None, help="First name")
@click.option("--last-name", default=None, help="Last name")
@click.option("--email", default=None, help="Email")
@click.pass_context
def user_update(ctx, pk, first_name, last_name, email):
    """Update a user."""
    try:
        client = _get_client(ctx)
        updates = {}
        if first_name:
            updates["first_name"] = first_name
        if last_name:
            updates["last_name"] = last_name
        if email:
            updates["email"] = email
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        data = client.update_user(pk, **updates)
        _output(ctx, data, lambda d: click.echo(f"User {pk} updated."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@user.command("delete")
@click.argument("pk", type=int)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
@click.pass_context
def user_delete(ctx, pk, confirm):
    """Delete a user."""
    if not confirm and not ctx.obj.get("json_mode"):
        click.confirm(f"Delete user {pk}?", abort=True)
    try:
        client = _get_client(ctx)
        data = client.delete_user(pk)
        _output(ctx, data, lambda d: click.echo(f"User {pk} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@user.command("me")
@click.pass_context
def user_me(ctx):
    """Show authenticated user info."""
    try:
        client = _get_client(ctx)
        data = client.get_user_info()
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Group Commands ───────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def group(ctx):
    """Group management commands."""
    pass


@group.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def group_list(ctx, page):
    """List groups."""
    try:
        client = _get_client(ctx)
        data = client.list_groups(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_group_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@group.command("info")
@click.argument("pk", type=int)
@click.pass_context
def group_info(ctx, pk):
    """Show group details."""
    try:
        client = _get_client(ctx)
        data = client.get_group(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@group.command("members")
@click.argument("pk", type=int)
@click.pass_context
def group_members(ctx, pk):
    """List group members."""
    try:
        client = _get_client(ctx)
        data = client.get_group_members(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@group.command("resources")
@click.argument("pk", type=int)
@click.pass_context
def group_resources(ctx, pk):
    """List resources owned by group."""
    try:
        client = _get_client(ctx)
        data = client.get_group_resources(pk)
        _output(ctx, data, format_resource_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@group.command("managers")
@click.argument("pk", type=int)
@click.pass_context
def group_managers(ctx, pk):
    """List group managers."""
    try:
        client = _get_client(ctx)
        data = client.get_group_managers(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Upload Commands ──────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def upload(ctx):
    """Upload monitoring commands."""
    pass


@upload.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def upload_list(ctx, page):
    """List recent uploads."""
    try:
        client = _get_client(ctx)
        data = client.list_uploads(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_upload_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@upload.command("status")
@click.argument("pk", type=int)
@click.pass_context
def upload_status(ctx, pk):
    """Check upload status."""
    try:
        client = _get_client(ctx)
        data = client.get_upload(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@upload.command("size-limits")
@click.pass_context
def upload_size_limits(ctx):
    """Show upload size limits."""
    try:
        client = _get_client(ctx)
        data = client.get_upload_size_limits()
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@upload.command("parallelism-limits")
@click.pass_context
def upload_parallelism_limits(ctx):
    """Show upload parallelism limits."""
    try:
        client = _get_client(ctx)
        data = client.get_upload_parallelism_limits()
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@upload.command("imports")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def upload_imports(ctx, page):
    """List imports via importer orchestrator."""
    try:
        client = _get_client(ctx)
        data = client.list_imports(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Execution Request Commands ───────────────────────────────────────────

@cli.group("execution")
@click.pass_context
def execution_group(ctx):
    """Async execution request commands."""
    pass


@execution_group.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def execution_list(ctx, page):
    """List execution requests."""
    try:
        client = _get_client(ctx)
        data = client.list_execution_requests(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_execution_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@execution_group.command("info")
@click.argument("exec_id")
@click.pass_context
def execution_info(ctx, exec_id):
    """Show execution request details."""
    try:
        client = _get_client(ctx)
        data = client.get_execution_request(exec_id)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@execution_group.command("status")
@click.argument("exec_id")
@click.pass_context
def execution_status(ctx, exec_id):
    """Check async operation status."""
    try:
        client = _get_client(ctx)
        data = client.get_execution_status(exec_id)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@execution_group.command("delete")
@click.argument("exec_id")
@click.pass_context
def execution_delete(ctx, exec_id):
    """Delete an execution request."""
    try:
        client = _get_client(ctx)
        data = client.delete_execution_request(exec_id)
        _output(ctx, data, lambda d: click.echo(f"Execution request {exec_id} deleted."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Harvester Commands ───────────────────────────────────────────────────

@cli.group()
@click.pass_context
def harvester(ctx):
    """Harvester management commands."""
    pass


@harvester.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def harvester_list(ctx, page):
    """List harvesters."""
    try:
        client = _get_client(ctx)
        data = client.list_harvesters(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_harvester_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@harvester.command("info")
@click.argument("pk", type=int)
@click.pass_context
def harvester_info(ctx, pk):
    """Show harvester details."""
    try:
        client = _get_client(ctx)
        data = client.get_harvester(pk)
        _output(ctx, data, format_resource_detail)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@harvester.command("create")
@click.option("--name", required=True, help="Harvester name")
@click.option("--url", "remote_url", required=True, help="Remote service URL")
@click.option("--type", "harvester_type", default=None, help="Harvester type")
@click.pass_context
def harvester_create(ctx, name, remote_url, harvester_type):
    """Create a new harvester."""
    try:
        client = _get_client(ctx)
        payload = {"name": name, "remote_url": remote_url}
        if harvester_type:
            payload["harvester_type"] = harvester_type
        data = client.create_harvester(**payload)
        _output(ctx, data, lambda d: click.echo(
            f"Harvester created: {d.get('pk', d.get('id', 'unknown'))}"))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@harvester.command("update")
@click.argument("pk", type=int)
@click.option("--name", default=None, help="New name")
@click.option("--url", "remote_url", default=None, help="New remote URL")
@click.pass_context
def harvester_update(ctx, pk, name, remote_url):
    """Update a harvester."""
    try:
        client = _get_client(ctx)
        updates = {}
        if name:
            updates["name"] = name
        if remote_url:
            updates["remote_url"] = remote_url
        if not updates:
            click.echo("No updates specified.", err=True)
            return
        data = client.update_harvester(pk, **updates)
        _output(ctx, data, lambda d: click.echo(f"Harvester {pk} updated."))
    except GeoNodeError as e:
        _handle_error(ctx, e)


@harvester.command("harvestable-resources")
@click.argument("pk", type=int)
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def harvester_resources(ctx, pk, page):
    """List harvestable resources for a harvester."""
    try:
        client = _get_client(ctx)
        data = client.get_harvestable_resources(pk, page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@harvester.command("sessions")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def harvester_sessions(ctx, page):
    """List harvesting sessions."""
    try:
        client = _get_client(ctx)
        data = client.list_harvesting_sessions(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@harvester.command("session-info")
@click.argument("pk", type=int)
@click.pass_context
def harvester_session_info(ctx, pk):
    """Show harvesting session details."""
    try:
        client = _get_client(ctx)
        data = client.get_harvesting_session(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Metadata Commands ────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def metadata(ctx):
    """Metadata management commands."""
    pass


@metadata.command("info")
@click.pass_context
def metadata_info(ctx):
    """Show metadata endpoints info."""
    try:
        client = _get_client(ctx)
        data = client.get_metadata_info()
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@metadata.command("schema")
@click.option("--pk", type=int, default=None, help="Specific schema PK")
@click.pass_context
def metadata_schema(ctx, pk):
    """Get JSON schema for metadata."""
    try:
        client = _get_client(ctx)
        data = client.get_metadata_schema(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@metadata.command("instance")
@click.argument("pk", type=int)
@click.option("--set-json", default=None, help="Update metadata from JSON")
@click.pass_context
def metadata_instance(ctx, pk, set_json):
    """Get or update metadata instance for a resource."""
    try:
        client = _get_client(ctx)
        if set_json:
            data_in = json_mod.loads(set_json)
            data = client.update_metadata_instance(pk, **data_in)
            _output(ctx, data, lambda d: click.echo(f"Metadata updated for resource {pk}."))
        else:
            data = client.get_metadata_instance(pk)
            _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@metadata.command("autocomplete")
@click.argument("entity", type=click.Choice([
    "users", "resources", "regions", "hkeywords",
    "groups", "categories", "licenses"]))
@click.option("--query", "-q", default="", help="Search query")
@click.pass_context
def metadata_autocomplete(ctx, entity, query):
    """Autocomplete for metadata fields."""
    try:
        client = _get_client(ctx)
        method_map = {
            "users": client.autocomplete_users,
            "resources": client.autocomplete_resources,
            "regions": client.autocomplete_regions,
            "hkeywords": client.autocomplete_keywords,
            "groups": client.autocomplete_groups,
            "categories": client.autocomplete_categories,
            "licenses": client.autocomplete_licenses,
        }
        data = method_map[entity](query)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Facet Commands ───────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def facet(ctx):
    """Faceted search commands."""
    pass


@facet.command("list")
@click.pass_context
def facet_list(ctx):
    """List all available facets."""
    try:
        client = _get_client(ctx)
        data = client.list_facets()
        _output(ctx, data, format_facet_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@facet.command("get")
@click.argument("name")
@click.option("--page", type=int, default=1, help="Page number")
@click.option("--lang", default=None, help="Language code")
@click.option("--contains", "topic_contains", default=None, help="Filter topics")
@click.pass_context
def facet_get(ctx, name, page, lang, topic_contains):
    """Get facet details with topics."""
    try:
        client = _get_client(ctx)
        data = client.get_facet(name, page=page, page_size=ctx.obj["page_size"],
                                 lang=lang, topic_contains=topic_contains)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Category Commands ────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def category(ctx):
    """Topic category commands."""
    pass


@category.command("list")
@click.pass_context
def category_list(ctx):
    """List topic categories."""
    try:
        client = _get_client(ctx)
        data = client.list_categories()
        _output(ctx, data, format_category_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@category.command("info")
@click.argument("pk", type=int)
@click.pass_context
def category_info(ctx, pk):
    """Show category details."""
    try:
        client = _get_client(ctx)
        data = client.get_category(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Region Commands ──────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def region(ctx):
    """Geographic region commands."""
    pass


@region.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def region_list(ctx, page):
    """List geographic regions."""
    try:
        client = _get_client(ctx)
        data = client.list_regions(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_region_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@region.command("info")
@click.argument("pk", type=int)
@click.pass_context
def region_info(ctx, pk):
    """Show region details."""
    try:
        client = _get_client(ctx)
        data = client.get_region(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Keyword Commands ─────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def keyword(ctx):
    """Keyword management commands."""
    pass


@keyword.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def keyword_list(ctx, page):
    """List hierarchical keywords."""
    try:
        client = _get_client(ctx)
        data = client.list_keywords(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data, format_keyword_list)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@keyword.command("info")
@click.argument("pk", type=int)
@click.pass_context
def keyword_info(ctx, pk):
    """Show keyword details."""
    try:
        client = _get_client(ctx)
        data = client.get_keyword(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@keyword.command("thesaurus")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def keyword_thesaurus(ctx, page):
    """List thesaurus keywords."""
    try:
        client = _get_client(ctx)
        data = client.list_thesaurus_keywords(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@keyword.command("thesaurus-info")
@click.argument("pk", type=int)
@click.pass_context
def keyword_thesaurus_info(ctx, pk):
    """Show thesaurus keyword details."""
    try:
        client = _get_client(ctx)
        data = client.get_thesaurus_keyword(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Owner Commands ───────────────────────────────────────────────────────

@cli.group()
@click.pass_context
def owner(ctx):
    """Resource owner commands."""
    pass


@owner.command("list")
@click.option("--page", type=int, default=1, help="Page number")
@click.pass_context
def owner_list(ctx, page):
    """List resource owners."""
    try:
        client = _get_client(ctx)
        data = client.list_owners(page=page, page_size=ctx.obj["page_size"])
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


@owner.command("info")
@click.argument("pk", type=int)
@click.pass_context
def owner_info(ctx, pk):
    """Show owner details."""
    try:
        client = _get_client(ctx)
        data = client.get_owner(pk)
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Schema Command ───────────────────────────────────────────────────────

@cli.command("schema")
@click.pass_context
def schema_cmd(ctx):
    """Get OpenAPI schema."""
    try:
        client = _get_client(ctx)
        data = client.get_openapi_schema()
        _output(ctx, data)
    except GeoNodeError as e:
        _handle_error(ctx, e)


# ── Entry point ──────────────────────────────────────────────────────────

def main():
    cli(auto_envvar_prefix="GEONODE")


if __name__ == "__main__":
    main()
