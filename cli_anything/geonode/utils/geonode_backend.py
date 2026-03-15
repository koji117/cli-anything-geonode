"""GeoNode backend — connection validator and version detection."""

import requests


def find_geonode(url="http://localhost:8000"):
    """Verify GeoNode is reachable at the given URL.

    Returns version info dict or raises RuntimeError with install instructions.
    """
    url = url.rstrip("/")
    api_url = f"{url}/api/v2/"
    try:
        resp = requests.get(api_url, timeout=10, headers={"Accept": "application/json"})
        if resp.status_code < 400:
            return {"url": url, "reachable": True, "status": resp.status_code}
    except requests.ConnectionError:
        pass

    raise RuntimeError(
        f"GeoNode is not reachable at {url}\n"
        "GeoNode is a web application that must be running. Start it with:\n"
        "  docker compose up -d          # if you have the GeoNode docker-compose\n"
        "  # or\n"
        "  docker run -d -p 8000:8000 geonode/geonode:latest\n\n"
        "Then set the URL:\n"
        "  cli-anything-geonode config set-url http://localhost:8000\n"
        "  cli-anything-geonode config set-token <your-api-key>"
    )


def detect_version(url="http://localhost:8000"):
    """Detect GeoNode version from the API."""
    url = url.rstrip("/")
    try:
        resp = requests.get(f"{url}/version.txt", timeout=10)
        if resp.status_code == 200:
            return resp.text.strip()
    except requests.ConnectionError:
        pass
    return "unknown"
