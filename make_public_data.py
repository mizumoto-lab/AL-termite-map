#!/usr/bin/env python3
import csv
import hashlib
import json
import math
import secrets
import shutil
from collections import Counter
from pathlib import Path

SECRET_FILE = Path("AU-termite-samples-secret.csv")
PUBLIC_FILE = Path("AU-termite-samples.csv")
GOOGLE_MY_MAPS_FILE = Path("google_my_maps_AU_sample.csv")
MAP_CONFIG_FILE = Path("map_config.json")
SALT_FILE = Path(".privacy_salt")
PRIVACY_RADIUS_M = 300.0
ALABAMA_COUNTRY_NAMES = {"", "USA", "US", "UNITED STATES", "UNITED STATES OF AMERICA"}

PUBLIC_FIELDS = [
    "AUT_ID",
    "date",
    "collector",
    "lat",
    "lon",
    "locality",
    "city",
    "state",
    "country",
    "genus",
    "species",
    "id_method",
    "id_by",
    "alate",
    "coordinate_generalized",
    "privacy_radius_m",
]
GOOGLE_MY_MAPS_FIELDS = (
    PUBLIC_FIELDS[:11]
    + ["scientific_name", "common_name"]
    + PUBLIC_FIELDS[11:]
)


def public_file_is_already_generalized():
    try:
        with PUBLIC_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return "coordinate_generalized" in (reader.fieldnames or [])
    except OSError:
        return False


def prepare_secret_file():
    if SECRET_FILE.exists():
        return
    if not PUBLIC_FILE.exists():
        raise SystemExit(
            f"Could not find {SECRET_FILE} or {PUBLIC_FILE}.\n"
            f"Put the exact specimen master in this folder as {SECRET_FILE} and run again."
        )
    if public_file_is_already_generalized():
        raise SystemExit(
            f"{PUBLIC_FILE} already contains privacy fields, but {SECRET_FILE} is missing.\n\n"
            f"Copy the exact specimen master into this folder as:\n"
            f"  {SECRET_FILE}\n"
            "and run the script again."
        )
    shutil.copy2(PUBLIC_FILE, SECRET_FILE)
    print(f"Created local private master: {SECRET_FILE}")
    print("This file is ignored by Git and must remain private.")


def load_or_create_salt():
    if SALT_FILE.exists():
        salt = SALT_FILE.read_text(encoding="utf-8").strip()
        if not salt:
            raise RuntimeError(f"{SALT_FILE} exists but is empty.")
        return salt
    salt = secrets.token_hex(32)
    SALT_FILE.write_text(salt + "\n", encoding="utf-8")
    print(f"Created local privacy salt: {SALT_FILE}")
    print("Keep this file private so public coordinates remain reproducible.")
    return salt


def parse_coordinates(row):
    try:
        lat = float(row.get("lat"))
        lon = float(row.get("lon"))
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return None
    if not (-90.0 < lat < 90.0 and -180.0 <= lon <= 180.0):
        return None
    return lat, lon


def deterministic_offset(record_id, salt):
    digest = hashlib.sha256(f"{salt}|{record_id}".encode("utf-8")).digest()
    u1 = int.from_bytes(digest[:8], "big") / 2**64
    u2 = int.from_bytes(digest[8:16], "big") / 2**64
    radius = PRIVACY_RADIUS_M * math.sqrt(u1)
    angle = 2.0 * math.pi * u2
    return radius * math.cos(angle), radius * math.sin(angle)


def shift_coordinate(lat, lon, east_m, north_m):
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lon = 111_320.0 * math.cos(math.radians(lat))
    if abs(meters_per_degree_lon) < 1e-12:
        raise ValueError("Longitude displacement is undefined at this latitude.")
    return (
        lat + north_m / meters_per_degree_lat,
        lon + east_m / meters_per_degree_lon,
    )


def record_key(row, lat, lon):
    record_id = (row.get("AUT_ID") or "").strip()
    if record_id:
        return record_id
    return "|".join([
        (row.get("date") or "").strip(),
        (row.get("genus") or "").strip(),
        (row.get("species") or "").strip(),
        f"{lat:.8f}",
        f"{lon:.8f}",
    ])


def duplicate_record_ids(rows):
    ids = [(row.get("AUT_ID") or "").strip() for row in rows]
    counts = Counter(record_id for record_id in ids if record_id)
    return sorted(record_id for record_id, count in counts.items() if count > 1)


def load_map_config():
    try:
        with MAP_CONFIG_FILE.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except OSError as error:
        raise SystemExit(f"Could not read {MAP_CONFIG_FILE}: {error}") from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"Could not parse {MAP_CONFIG_FILE}: {error}") from error
    if not config.get("valid_species"):
        raise SystemExit(f"{MAP_CONFIG_FILE} does not define valid_species.")
    return config


def valid_taxa(config):
    return {
        tuple(name.split(" ", 1))
        for name in config["valid_species"]
        if isinstance(name, str) and " " in name
    }


def invalid_taxa(rows, accepted_taxa):
    invalid = []
    for row in rows:
        genus = (row.get("genus") or "").strip()
        species = (row.get("species") or "").strip()
        if (genus, species) not in accepted_taxa:
            invalid.append(((row.get("AUT_ID") or "").strip(), genus, species))
    return invalid


def public_row(row, salt):
    out = {field: "" for field in PUBLIC_FIELDS}
    for field in [
        "AUT_ID",
        "date",
        "collector",
        "state",
        "country",
        "genus",
        "species",
        "id_method",
        "id_by",
        "alate",
    ]:
        out[field] = (row.get(field) or "").strip()
    coordinates = parse_coordinates(row)
    if coordinates:
        lat, lon = coordinates
        east_m, north_m = deterministic_offset(record_key(row, lat, lon), salt)
        public_lat, public_lon = shift_coordinate(lat, lon, east_m, north_m)
        out["lat"] = f"{public_lat:.6f}"
        out["lon"] = f"{public_lon:.6f}"
        out["coordinate_generalized"] = "yes"
        out["privacy_radius_m"] = str(int(PRIVACY_RADIUS_M))
    else:
        out["coordinate_generalized"] = "no_coordinate"
    return out


def canonical_name(row):
    return " ".join(
        part
        for part in [
            (row.get("genus") or "").strip(),
            (row.get("species") or "").strip(),
        ]
        if part
    )


def is_alabama_map_record(row):
    if (row.get("state") or "").strip().upper() != "AL":
        return False
    country = (row.get("country") or "").strip().upper()
    if country not in ALABAMA_COUNTRY_NAMES:
        return False
    coordinates = parse_coordinates(row)
    if not coordinates:
        return False
    lat, lon = coordinates
    return 30.1 <= lat <= 35.2 and -88.6 <= lon <= -84.8


def google_my_maps_row(row, config):
    name = canonical_name(row)
    scientific_name = config.get("scientific_display_names", {}).get(name, name)
    common_name = config.get("scientific_common_names", {}).get(name)
    if not common_name and (row.get("genus") or "").strip() == "Reticulitermes":
        common_name = "Native subterranean termite"
    if not common_name:
        genus = (row.get("genus") or "").strip()
        common_name = config.get("taxa", {}).get(genus, {}).get("display_name", "")
    if not scientific_name or not common_name:
        raise RuntimeError(f"Could not determine map names for {name or '<blank taxon>'}.")
    out = {field: (row.get(field) or "").strip() for field in PUBLIC_FIELDS}
    out["scientific_name"] = scientific_name
    out["common_name"] = common_name
    return out


def write_google_my_maps_file(public_rows, config):
    accepted_names = set(config["valid_species"])
    rows = [
        google_my_maps_row(row, config)
        for row in public_rows
        if is_alabama_map_record(row) and canonical_name(row) in accepted_names
    ]
    with GOOGLE_MY_MAPS_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GOOGLE_MY_MAPS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    prepare_secret_file()
    salt = load_or_create_salt()
    config = load_map_config()
    with SECRET_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    duplicates = duplicate_record_ids(rows)
    accepted_taxa = valid_taxa(config)
    invalid = invalid_taxa(rows, accepted_taxa)
    public_rows = [public_row(row, salt) for row in rows]
    with PUBLIC_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PUBLIC_FIELDS)
        writer.writeheader()
        writer.writerows(public_rows)
    google_my_maps_rows = write_google_my_maps_file(public_rows, config)
    generalized = sum(parse_coordinates(row) is not None for row in rows)
    without_coordinates = len(rows) - generalized
    print()
    print(f"Created public file: {PUBLIC_FILE}")
    print(f"Rows written: {len(public_rows)}")
    print(f"Coordinates generalized within {int(PRIVACY_RADIUS_M)} m: {generalized}")
    print(f"Rows without valid coordinates: {without_coordinates}")
    print("Locality and city are omitted from all public specimen rows.")
    print()
    print(f"Created Google My Maps file: {GOOGLE_MY_MAPS_FILE}")
    print(f"Alabama map records written: {google_my_maps_rows}")
    if duplicates:
        print()
        print("WARNING: Duplicate AUT_ID values found in the private master:")
        for record_id in duplicates:
            print(f"  {record_id}")
    if invalid:
        print()
        print("WARNING: Unrecognized taxon names found in the private master:")
        for record_id, genus, species in invalid:
            name = " ".join(part for part in [genus, species] if part) or "<blank>"
            print(f"  {record_id or '<no AUT_ID>'}: {name}")
        print("Valid public taxa are:")
        for genus, species in sorted(accepted_taxa):
            label = f"{genus} {species}"
            if label == "Reticulitermes nelsonae":
                label += " (complex)"
            print(f"  {label}")
    print()
    print(f"Commit/push {PUBLIC_FILE} and {GOOGLE_MY_MAPS_FILE}.")
    print(f"Keep {SECRET_FILE} and {SALT_FILE} local/private.")


if __name__ == "__main__":
    main()
