"""Output formatters for GeoNode CLI — human-readable display helpers."""

import click


def format_resource_list(data, resource_type="resources"):
    """Print a paginated list of resources."""
    resources = data.get(resource_type, data.get("results", []))
    total = data.get("total", len(resources))

    if not resources:
        click.echo(f"No {resource_type} found.")
        return

    click.echo(f"{'ID':<8} {'Title':<40} {'Owner':<15} {'Type':<12}")
    click.echo("-" * 75)
    for r in resources:
        pk = r.get("pk", r.get("id", ""))
        title = str(r.get("title", ""))[:38]
        owner = str(r.get("owner", {}).get("username", r.get("owner", "")))[:13]
        rtype = str(r.get("resource_type", r.get("polymorphic_ctype", "")))[:10]
        click.echo(f"{pk:<8} {title:<40} {owner:<15} {rtype:<12}")

    click.echo(f"\nShowing {len(resources)} of {total} total")


def format_dataset_list(data):
    """Print dataset list."""
    format_resource_list(data, "datasets")


def format_map_list(data):
    """Print map list."""
    format_resource_list(data, "maps")


def format_document_list(data):
    """Print document list."""
    format_resource_list(data, "documents")


def format_resource_detail(data):
    """Print resource detail as key-value pairs."""
    fields = [
        "pk", "title", "abstract", "owner", "resource_type", "date",
        "date_type", "edition", "purpose", "category", "regions",
        "keywords", "bbox_polygon", "srid", "is_published", "is_approved",
        "detail_url", "thumbnail_url",
    ]
    for key in fields:
        if key in data:
            val = data[key]
            if isinstance(val, dict):
                val = val.get("username", val.get("identifier", str(val)))
            elif isinstance(val, list):
                val = ", ".join(str(v.get("name", v) if isinstance(v, dict) else v) for v in val[:5])
                if len(data[key]) > 5:
                    val += f" ... ({len(data[key])} total)"
            click.echo(f"  {key:<20} {val}")


def format_user_list(data):
    """Print user list."""
    users = data.get("users", data.get("results", []))
    if not users:
        click.echo("No users found.")
        return
    click.echo(f"{'ID':<8} {'Username':<20} {'Name':<25} {'Active':<8}")
    click.echo("-" * 61)
    for u in users:
        pk = u.get("pk", u.get("id", ""))
        username = str(u.get("username", ""))[:18]
        name = f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()[:23]
        active = "Yes" if u.get("is_active", True) else "No"
        click.echo(f"{pk:<8} {username:<20} {name:<25} {active:<8}")


def format_group_list(data):
    """Print group list."""
    groups = data.get("groups", data.get("results", []))
    if not groups:
        click.echo("No groups found.")
        return
    click.echo(f"{'ID':<8} {'Title':<30} {'Access':<15}")
    click.echo("-" * 53)
    for g in groups:
        pk = g.get("pk", g.get("id", ""))
        title = str(g.get("title", g.get("name", "")))[:28]
        access = str(g.get("access", ""))[:13]
        click.echo(f"{pk:<8} {title:<30} {access:<15}")


def format_permissions(data):
    """Print permissions."""
    if not data:
        click.echo("No permissions data.")
        return
    for key, val in data.items():
        if isinstance(val, list):
            click.echo(f"  {key}:")
            for item in val:
                click.echo(f"    - {item}")
        else:
            click.echo(f"  {key}: {val}")


def format_upload_list(data):
    """Print upload list."""
    uploads = data.get("uploads", data.get("results", []))
    if not uploads:
        click.echo("No uploads found.")
        return
    click.echo(f"{'ID':<8} {'Name':<30} {'State':<15} {'Date':<20}")
    click.echo("-" * 73)
    for u in uploads:
        pk = u.get("id", u.get("pk", ""))
        name = str(u.get("name", u.get("title", "")))[:28]
        state = str(u.get("state", u.get("status", "")))[:13]
        date = str(u.get("date", u.get("created", "")))[:18]
        click.echo(f"{pk:<8} {name:<30} {state:<15} {date:<20}")


def format_config(config):
    """Print config key-value pairs."""
    for key, val in config.items():
        click.echo(f"  {key:<15} {val}")


def format_geoapp_list(data):
    """Print geoapp list."""
    format_resource_list(data, "geoapps")


def format_harvester_list(data):
    """Print harvester list."""
    harvesters = data.get("harvesters", data.get("results", []))
    if not harvesters:
        click.echo("No harvesters found.")
        return
    click.echo(f"{'ID':<8} {'Name':<30} {'URL':<35}")
    click.echo("-" * 73)
    for h in harvesters:
        pk = h.get("pk", h.get("id", ""))
        name = str(h.get("name", ""))[:28]
        url = str(h.get("remote_url", ""))[:33]
        click.echo(f"{pk:<8} {name:<30} {url:<35}")


def format_execution_list(data):
    """Print execution request list."""
    items = data.get("requests", data.get("results", []))
    if not items:
        click.echo("No execution requests found.")
        return
    click.echo(f"{'ID':<38} {'Action':<15} {'Status':<12} {'Created':<20}")
    click.echo("-" * 85)
    for e in items:
        eid = str(e.get("exec_id", e.get("id", "")))[:36]
        action = str(e.get("action", ""))[:13]
        status = str(e.get("status", ""))[:10]
        created = str(e.get("created", ""))[:18]
        click.echo(f"{eid:<38} {action:<15} {status:<12} {created:<20}")


def format_facet_list(data):
    """Print facet list."""
    facets = data.get("facets", data.get("results", []))
    if isinstance(facets, list):
        if not facets:
            click.echo("No facets found.")
            return
        for f in facets:
            if isinstance(f, dict):
                click.echo(f"  {f.get('name', f.get('label', str(f)))}")
            else:
                click.echo(f"  {f}")
    elif isinstance(facets, dict):
        for name, info in facets.items():
            click.echo(f"  {name}")
    else:
        click.echo(str(data))


def format_category_list(data):
    """Print category list."""
    categories = data.get("categories", data.get("results", []))
    if not categories:
        click.echo("No categories found.")
        return
    click.echo(f"{'ID':<8} {'Identifier':<25} {'Description':<40}")
    click.echo("-" * 73)
    for c in categories:
        pk = c.get("pk", c.get("id", ""))
        ident = str(c.get("identifier", c.get("slug", "")))[:23]
        desc = str(c.get("description", c.get("gn_description", "")))[:38]
        click.echo(f"{pk:<8} {ident:<25} {desc:<40}")


def format_region_list(data):
    """Print region list."""
    regions = data.get("regions", data.get("results", []))
    if not regions:
        click.echo("No regions found.")
        return
    click.echo(f"{'ID':<8} {'Code':<10} {'Name':<40}")
    click.echo("-" * 58)
    for r in regions:
        pk = r.get("pk", r.get("id", ""))
        code = str(r.get("code", ""))[:8]
        name = str(r.get("name", ""))[:38]
        click.echo(f"{pk:<8} {code:<10} {name:<40}")


def format_keyword_list(data):
    """Print keyword list."""
    keywords = data.get("keywords", data.get("results", []))
    if not keywords:
        click.echo("No keywords found.")
        return
    click.echo(f"{'ID':<8} {'Name':<30} {'Slug':<30}")
    click.echo("-" * 68)
    for k in keywords:
        pk = k.get("pk", k.get("id", ""))
        name = str(k.get("name", ""))[:28]
        slug = str(k.get("slug", ""))[:28]
        click.echo(f"{pk:<8} {name:<30} {slug:<30}")
