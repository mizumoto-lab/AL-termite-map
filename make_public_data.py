#!/usr/bin/env python3
"""Build the public termite-map CSV from a local exact-coordinate master CSV.

First run
---------
If ``AU-termite-samples-secret.csv`` does not exist but
``AU-termite-samples.csv`` does, the script copies the current CSV to the
secret filename before generating the public file. This makes the initial
conversion a one-click operation.

Privacy rule
------------
* ``Coptotermes formosanus`` coordinates are displaced by up to 300 m.
* The same AUT_ID receives the same displacement on future runs because the
  offset is derived from a local secret salt.
* FST locality/city text is removed from the public file so address-like text
  cannot expose a property.
* Only fields used by the public map are written.

Never commit ``AU-termite-samples-secret.csv`` or ``.privacy_salt``.
"""

import csv
import hashlib
import math
import secrets
import shutil
from pathlib import Path

SECRET_FILE = Path("AU-termite-samples-secret.csv")
PUBLIC_FILE = Path("AU-termite-samples.csv")
SALT_FILE = Path(".privacy_salt")
JITTER_RADIUS_M = 300.0

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
    "coordinate_generalized",
    "privacy_radius_m",
]


def prepare_secret_file():
    if SECRET_FILE.exists():
        return
    if not PUBLIC_FILE.exists():
        raise SystemExit(
            f"Could not find {SECRET_FILE} or {PUBLIC_FILE}.\n"
            "Put your exact master CSV in this folder and run again."
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


def valid_coordinate(value):
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def is_fst(row):
    genus = (row.get("genus") or "").strip().lower()
    species = (row.get("species") or "").strip().lower()
    return genus == "coptotermes" and species == "formosanus"


def deterministic_offset(record_id, salt):
    """Return a stable random east/north offset uniformly within a 300 m disk."""
    digest = hashlib.sha256(f"{salt}|{record_id}".encode("utf-8")).digest()
    u1 = int.from_bytes(digest[:8], "big") / 2**64
    u2 = int.from_bytes(digest[8:16], "big") / 2**64

    radius = JITTER_RADIUS_M * math.sqrt(u1)
    angle = 2.0 * math.pi * u2
    return radius * math.cos(angle), radius * math.sin(angle)


def shift_coordinate(lat, lon, east_m, north_m):
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lon = 111_320.0 * math.cos(math.radians(lat))
    return (
        lat + north_m / meters_per_degree_lat,
        lon + east_m / meters_per_degree_lon,
    )


def public_row(row, salt):
    out = {field: "" for field in PUBLIC_FIELDS}
    for field in [
        "AUT_ID", "date", "lat", "lon", "locality", "city",
        "state", "country", "genus", "species"
    ]:
        out[field] = (row.get(field) or "").strip()

    if is_fst(row):
        # FST is the privacy-sensitive taxon. Do not expose locality/address text.
        out["locality"] = ""
        out["city"] = ""

        if valid_coordinate(row.get("lat")) and valid_coordinate(row.get("lon")):
            lat = float(row["lat"])
            lon = float(row["lon"])
            record_id = (row.get("AUT_ID") or "").strip()
            if not record_id:
                record_id = f"{row.get('date', '')}|{lat:.8f}|{lon:.8f}"

            east_m, north_m = deterministic_offset(record_id, salt)
            public_lat, public_lon = shift_coordinate(lat, lon, east_m, north_m)
            out["lat"] = f"{public_lat:.6f}"
            out["lon"] = f"{public_lon:.6f}"
            out["coordinate_generalized"] = "yes"
            out["privacy_radius_m"] = str(int(JITTER_RADIUS_M))
        else:
            out["coordinate_generalized"] = "no_coordinate"

    return out


def main():
    prepare_secret_file()
    salt = load_or_create_salt()

    with SECRET_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    public_rows = [public_row(row, salt) for row in rows]

    with PUBLIC_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PUBLIC_FIELDS)
        writer.writeheader()
        writer.writerows(public_rows)

    fst_total = sum(is_fst(row) for row in rows)
    generalized = sum(
        is_fst(row)
        and valid_coordinate(row.get("lat"))
        and valid_coordinate(row.get("lon"))
        for row in rows
    )

    print()
    print(f"Created public file: {PUBLIC_FILE}")
    print(f"Rows written: {len(public_rows)}")
    print(f"FST records: {fst_total}")
    print(f"FST coordinates generalized within 300 m: {generalized}")
    print()
    print("Commit/push AU-termite-samples.csv only.")
    print(f"Keep {SECRET_FILE} and {SALT_FILE} local/private.")


if __name__ == "__main__":
    main()
