from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.exceptions import ExternalServiceError

DEFAULT_ADMIN_LEVELS = ("2", "4", "5", "6")


async def fetch_admin_boundaries(
    *,
    west: float,
    south: float,
    east: float,
    north: float,
    admin_levels: tuple[str, ...] = DEFAULT_ADMIN_LEVELS,
    settings: Settings,
) -> dict[str, Any]:
    query = build_overpass_query(
        west=west,
        south=south,
        east=east,
        north=north,
        admin_levels=admin_levels,
    )
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                settings.overpass_url,
                data={"data": query},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "floodguard-backend/0.1",
                },
            )
    except httpx.TimeoutException as exc:
        raise ExternalServiceError("Administrative boundary request timed out") from exc
    except httpx.HTTPError as exc:
        raise ExternalServiceError(
            "Administrative boundary request failed",
            details={"error": str(exc)},
        ) from exc

    if response.status_code >= 400:
        raise ExternalServiceError(
            "Administrative boundary API returned an error",
            details={"status_code": response.status_code, "body": response.text[:1000]},
        )
    return overpass_to_geojson(
        response.json(),
        label_lon=(west + east) / 2,
        label_lat=(south + north) / 2,
    )


def build_overpass_query(
    *,
    west: float,
    south: float,
    east: float,
    north: float,
    admin_levels: tuple[str, ...] = DEFAULT_ADMIN_LEVELS,
) -> str:
    levels = "|".join(admin_levels)
    center_lat = (south + north) / 2
    center_lon = (west + east) / 2
    return f"""
[out:json][timeout:25];
(
  relation["boundary"="administrative"]["admin_level"~"^({levels})$"]({south},{west},{north},{east});
);
out geom;
is_in({center_lat},{center_lon})->.admin_areas;
rel(pivot.admin_areas)["boundary"="administrative"]["admin_level"~"^({levels})$"];
out tags center;
""".strip()


def overpass_to_geojson(
    payload: dict[str, Any],
    *,
    label_lon: float | None = None,
    label_lat: float | None = None,
) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    containing_regions: list[tuple[int, str]] = []

    for relation in payload.get("elements", []):
        if relation.get("type") != "relation":
            continue
        tags = relation.get("tags", {})
        relation_id = int(relation.get("id", 0))
        admin_level = tags.get("admin_level")
        name = tags.get("name") or tags.get("int_name")
        if "center" in relation and name and admin_level:
            containing_regions.append((int(admin_level), str(name)))
        for member_index, member in enumerate(relation.get("members", [])):
            geometry = member.get("geometry")
            if member.get("type") != "way" or not geometry:
                continue
            member_id = int(member.get("ref", member_index))
            key = (relation_id, member_id)
            if key in seen:
                continue
            seen.add(key)
            coordinates = [
                [float(point["lon"]), float(point["lat"])]
                for point in geometry
                if "lat" in point and "lon" in point
            ]
            if len(coordinates) < 2:
                continue
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": relation_id,
                        "name": name,
                        "admin_level": admin_level,
                        "boundary": tags.get("boundary"),
                        "kind": "admin_boundary",
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates,
                    },
                }
            )

    if label_lon is not None and label_lat is not None and containing_regions:
        deduped = sorted(set(containing_regions), key=lambda item: item[0])
        names = [name for _, name in deduped]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": " / ".join(names),
                    "admin_names": names,
                    "kind": "admin_label",
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [label_lon, label_lat],
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}
