#!/usr/bin/env python3
import argparse
import csv
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

COUNTY_FILE = Path("alabama_counties.geojson")
INAT_FILE = Path("iNaturalist_records.csv")
META_FILE = Path("external_data_snapshot.json")
FOCAL_GENERA = ["Coptotermes", "Reticulitermes", "Kalotermes", "Incisitermes"]
COUNTY_ENDPOINT = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/19/query"
INAT_ENDPOINT = "https://api.inaturalist.org/v1/observations"
USER_AGENT = "AlabamaTermiteMap/0.1 (https://github.com/mizumoto-lab/AL-termite-map)"
BBOX = {"swlat": "30.1", "swlng": "-88.6", "nelat": "35.2", "nelng": "-84.8"}


def request_json(url, params=None, timeout=60):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def download_counties():
    params = {
        "where": "STATE='01'",
        "outFields": "GEOID,BASENAME,NAME",
        "returnGeometry": "true",
        "outSR": "4326",
        "geometryPrecision": "5",
        "maxAllowableOffset": "0.0005",
        "f": "geojson",
    }
    data = request_json(COUNTY_ENDPOINT, params=params)
    if "error" in data:
        raise RuntimeError(f"Census TIGERweb error: {data['error']}")
    features = data.get("features", [])
    if len(features) != 67:
        raise RuntimeError(f"Expected 67 Alabama counties, received {len(features)}.")
    tmp = COUNTY_FILE.with_suffix(".geojson.tmp")
    tmp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    tmp.replace(COUNTY_FILE)
    print(f"Saved {len(features)} Alabama counties to {COUNTY_FILE}")
    return data


def load_counties():
    with COUNTY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def point_in_ring(lon, lat, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]
        xj, yj = ring[j][:2]
        if (yi > lat) != (yj > lat):
            denom = yj - yi
            if denom != 0:
                x_cross = (xj - xi) * (lat - yi) / denom + xi
                if lon < x_cross:
                    inside = not inside
        j = i
    return inside


def point_in_polygon(lon, lat, polygon):
    if not polygon or not point_in_ring(lon, lat, polygon[0]):
        return False
    return not any(point_in_ring(lon, lat, hole) for hole in polygon[1:])


def point_in_alabama(lon, lat, counties):
    for feature in counties.get("features", []):
        geom = feature.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if geom.get("type") == "Polygon" and point_in_polygon(lon, lat, coords):
            return True
        if geom.get("type") == "MultiPolygon" and any(point_in_polygon(lon, lat, polygon) for polygon in coords):
            return True
    return False


def fetch_inat_genus(genus, counties):
    records = []
    page = 1
    total = None
    received = 0
    while total is None or received < total:
        params = {
            "taxon_name": genus,
            "quality_grade": "research",
            "geo": "true",
            **BBOX,
            "per_page": "200",
            "page": str(page),
            "order_by": "id",
            "order": "asc",
        }
        data = request_json(INAT_ENDPOINT, params=params)
        total = int(data.get("total_results") or 0)
        results = data.get("results") or []
        if not results:
            break
        received += len(results)
        for obs in results:
            license_code = obs.get("license_code") or obs.get("license") or ""
            if not license_code:
                continue
            geo = obs.get("geojson") or {}
            coords = geo.get("coordinates") or []
            if len(coords) < 2:
                continue
            try:
                lon = float(coords[0])
                lat = float(coords[1])
            except (TypeError, ValueError):
                continue
            if not (math.isfinite(lat) and math.isfinite(lon)):
                continue
            if not point_in_alabama(lon, lat, counties):
                continue
            taxon = obs.get("taxon") or {}
            user = obs.get("user") or {}
            obs_id = obs.get("id", "")
            records.append({
                "id": obs_id,
                "genus": genus,
                "name": taxon.get("name") or obs.get("species_guess") or genus,
                "lat": f"{lat:.6f}",
                "lon": f"{lon:.6f}",
                "observed_on": obs.get("observed_on") or "",
                "place": obs.get("place_guess") or "",
                "observer": user.get("login") or "",
                "license": license_code,
                "url": f"https://www.inaturalist.org/observations/{obs_id}" if obs_id else "",
            })
        print(f"{genus}: API page {page}, {len(records)} licensed Alabama observations retained.")
        page += 1
        time.sleep(1.0)
        if page > 100:
            raise RuntimeError(f"Unexpected pagination for {genus}.")
    return records


def write_inat(records):
    fields = ["id", "genus", "name", "lat", "lon", "observed_on", "place", "observer", "license", "url"]
    records.sort(key=lambda row: (row["genus"], row["name"], str(row["id"])))
    tmp = INAT_FILE.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    tmp.replace(INAT_FILE)
    print(f"Saved {len(records)} observations to {INAT_FILE}")


def load_previous_meta():
    if not META_FILE.exists():
        return {}
    try:
        with META_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-counties", action="store_true", help="Download Alabama county geometry again.")
    args = parser.parse_args()
    previous = load_previous_meta()
    now = datetime.now(timezone.utc)
    date = now.date().isoformat()
    county_refreshed = False
    if args.refresh_counties or not COUNTY_FILE.exists():
        counties = download_counties()
        county_date = date
        county_refreshed = True
    else:
        counties = load_counties()
        county_date = previous.get("counties", {}).get("downloaded") or "existing local snapshot"
        print(f"Using existing county file: {COUNTY_FILE}")
    records = []
    for genus in FOCAL_GENERA:
        records.extend(fetch_inat_genus(genus, counties))
    write_inat(records)
    metadata = {
        "updated": date,
        "generated_at_utc": now.isoformat(timespec="seconds"),
        "inaturalist": {
            "snapshot_date": date,
            "quality_grade": "research",
            "license_filter": "licensed observations only",
            "genera": FOCAL_GENERA,
            "records": len(records),
            "source": "iNaturalist API",
        },
        "counties": {
            "downloaded": county_date,
            "refreshed_this_run": county_refreshed,
            "features": len(counties.get("features", [])),
            "source": "U.S. Census Bureau TIGERweb",
        },
    }
    META_FILE.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print()
    print("Update complete.")
    print(f"Snapshot date: {date}")
    print(f"Licensed iNaturalist records: {len(records)}")
    print()
    print("Commit these files:")
    print(f"  {INAT_FILE}")
    print(f"  {META_FILE}")
    if county_refreshed:
        print(f"  {COUNTY_FILE}")


if __name__ == "__main__":
    main()
