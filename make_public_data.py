#!/usr/bin/env python3
import csv
import hashlib
import math
import secrets
import shutil
from collections import Counter
from pathlib import Path

SECRET_FILE = Path("AU-termite-samples-secret.csv")
PUBLIC_FILE = Path("AU-termite-samples.csv")
SALT_FILE = Path(".privacy_salt")
PRIVACY_RADIUS_M = 300.0

VALID_TAXA = {
    ("Reticulitermes", "flavipes"),
    ("Reticulitermes", "hageni"),
    ("Reticulitermes", "malletei"),
    ("Reticulitermes", "nelsonae"),
    ("Reticulitermes", "sp"),
    ("Reticulitermes", "virginicus"),
    ("Coptotermes", "formosanus"),
    ("Kalotermes", "approximatus"),
    ("Incisitermes", "snyderi"),
}

PUBLIC_FIELDS = [
    "AUT_ID",
    "date",
    "lat",
    "lon",
    "locality",
    "city",
    "state",
    "country",
    "genus",
    "species",
    "alate",
    "coordinate_generalized",
    "privacy_radius_m",
]


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


def invalid_taxa(rows):
    invalid = []
    for row in rows:
        genus = (row.get("genus") or "").strip()
        species = (row.get("species") or "").strip()
        if (genus, species) not in VALID_TAXA:
            invalid.append(((row.get("AUT_ID") or "").strip(), genus, species))
    return invalid


def public_row(row, salt):
    out = {field: "" for field in PUBLIC_FIELDS}
    for field in ["AUT_ID", "date", "state", "country", "genus", "species", "alate"]:
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


def main():
    prepare_secret_file()
    salt = load_or_create_salt()
    with SECRET_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    duplicates = duplicate_record_ids(rows)
    invalid = invalid_taxa(rows)
    public_rows = [public_row(row, salt) for row in rows]
    with PUBLIC_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PUBLIC_FIELDS)
        writer.writeheader()
        writer.writerows(public_rows)
    generalized = sum(parse_coordinates(row) is not None for row in rows)
    without_coordinates = len(rows) - generalized
    print()
    print(f"Created public file: {PUBLIC_FILE}")
    print(f"Rows written: {len(public_rows)}")
    print(f"Coordinates generalized within {int(PRIVACY_RADIUS_M)} m: {generalized}")
    print(f"Rows without valid coordinates: {without_coordinates}")
    print("Locality and city are omitted from all public specimen rows.")
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
        for genus, species in sorted(VALID_TAXA):
            label = f"{genus} {species}"
            if label == "Reticulitermes nelsonae":
                label += " (complex)"
            print(f"  {label}")
    print()
    print("Commit/push AU-termite-samples.csv only.")
    print(f"Keep {SECRET_FILE} and {SALT_FILE} local/private.")


if __name__ == "__main__":
    main()
