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
    format_config,
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
        "config show": "Show current connection config",
        "config test": "Test connection to GeoNode",
        "config set-url <url>": "Set GeoNode instance URL",
        "config set-token <token>": "Set API key / OAuth token",
        "dataset list": "List datasets",
        "dataset info <id>": "Show dataset details",
        "dataset upload <file>": "Upload a geospatial dataset",
        "dataset delete <id>": "Delete a dataset",
        "map list": "List maps",
        "map info <id>": "Show map details",
        "map create --title <t>": "Create a new map",
        "document list": "List documents",
        "document info <id>": "Show document details",
        "document upload <file>": "Upload a document",
        "resource list": "List all resources",
        "resource search <query>": "Search resources",
        "user list": "List users",
        "group list": "List groups",
        "upload list": "List recent uploads",
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


# ── Entry point ──────────────────────────────────────────────────────────

def main():
    cli(auto_envvar_prefix="GEONODE")


if __name__ == "__main__":
    main()
