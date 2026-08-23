# Alabama Termite Map

Static public map of documented termite records in Alabama.

## Version 0

Version 0 uses Leaflet in a single `index.html` file with static repository data. There is no database or server-side application.

The public-facing taxa are:

- Formosan subterranean termite (*Coptotermes formosanus*)
- Native subterranean termites (*Reticulitermes* spp.)
- Dark southern drywood termite (*Kalotermes approximatus*)
- Southeastern drywood termite (*Incisitermes snyderi*)

The default view shows Formosan subterranean termite, published county records, and verified museum specimens. The iNaturalist layer is off by default and `iNaturalist_records.csv` is requested only when that layer is enabled.

## Repository files

```text
index.html
map_config.json
README.md
.gitignore

AU-termite-samples.csv
FSTrecords.csv
alabama_counties.geojson
iNaturalist_records.csv
external_data_snapshot.json

make_public_data.py
make_public_data.bat
update_external_data.py
update_external_data.bat
```

## Map configuration

`map_config.json` contains the display settings that are most likely to be adjusted later without editing `index.html`.

It currently controls:

- default taxon and layer visibility
- taxon labels and colors
- species-specific colors
- published county polygon styling
- verified-specimen uncertainty-circle opacity and line width
- iNaturalist point radius, opacity, and line width

The physical radius of a verified-specimen privacy circle is not a display setting. It comes from `privacy_radius_m` in `AU-termite-samples.csv` because that radius describes location uncertainty and must match the privacy-processing step.

## Data sources

### Verified museum specimens

`AU-termite-samples.csv` is the public, privacy-filtered map input derived from the local exact specimen master associated with the Auburn University Natural History Museum and Alabama Termite Identification Service.

All museum records with coordinates are privacy-generalized before publication:

- the public coordinate is displaced by up to 300 m
- the displacement is deterministic when the same local `.privacy_salt` is reused
- `locality` and `city` are omitted from the public CSV
- `coordinate_generalized=yes`
- `privacy_radius_m=300`

The map renders public museum locations as translucent 300 m-radius circles with no center point. The circle is a public location-uncertainty area only. It is not biological range, territory, colony size, or infestation extent.

`index.html` intentionally does not plot legacy museum rows that still contain coordinates but do not have `coordinate_generalized=yes`. Regenerate `AU-termite-samples.csv` with the privacy workflow before publishing those records.

### Published Formosan subterranean termite county records

`FSTrecords.csv` contains county-level first-detection records from:

Hu, X. P. & Mizumoto, N. (2026, in press). *Four decades of inland invasion by Formosan subterranean termite in Alabama: expansion associated with transportation infrastructure.* Preprint: https://doi.org/10.32942/X21H4M

County shading indicates documented occurrence in a county. It should not be interpreted as occurrence throughout the county or as evidence of absence from unshaded counties.

### iNaturalist

`iNaturalist_records.csv` is a static snapshot. Normal website visitors do not query the iNaturalist API.

The updater requests Research Grade observations for the focal genera, retains only observations whose coordinates fall inside the locally stored Alabama county polygons, and retains only observations with an observation license. The CSV stores observation ID, genus, taxon name, coordinates, observed date, place, observer, observation license, and the original observation URL.

The website describes these as Research Grade/community-assessed observations and states that they are not independently verified by the Alabama Termite Identification Service. The snapshot date displayed on the website comes from `external_data_snapshot.json`.

The layer is lazy-loaded. Turning it off and back on after the CSV has already loaded redraws the cached records without making another request. A full page reload resets the checkbox to the configured default, which is currently off.

### County boundaries and basemap

`alabama_counties.geojson` is a static local snapshot of Alabama's 67 counties from the U.S. Census Bureau TIGERweb service. Normal website visitors do not query TIGERweb.

OpenStreetMap tiles are requested normally by the Leaflet basemap.

## Privacy workflow

The exact specimen master and privacy salt must remain local/private:

```text
AU-termite-samples-secret.csv
.privacy_salt
```

Both are listed in `.gitignore` and must never be committed.

To generate the public museum CSV on Windows:

1. Put the exact specimen master in the repository folder as `AU-termite-samples-secret.csv`.
2. Keep the existing `.privacy_salt` if one already exists. Reusing it keeps generalized positions stable between runs.
3. Double-click `make_public_data.bat`.
4. Review the regenerated `AU-termite-samples.csv`.
5. Commit only the public CSV, not the secret master or salt.

The current privacy generator applies the same 300 m generalization to all specimen taxa with valid coordinates.

If the public CSV already contains privacy fields and the exact secret master is missing, `make_public_data.py` intentionally stops rather than treating previously generalized coordinates as the exact master.

## External-data update workflow

Normal monthly updating is manual.

Double-click `update_external_data.bat`, or run:

```text
python update_external_data.py
```

Normal behavior:

- reuse `alabama_counties.geojson` when it already exists
- download Alabama's 67 counties from TIGERweb if the county file is missing
- download a fresh licensed Research Grade iNaturalist snapshot for `Coptotermes`, `Reticulitermes`, `Kalotermes`, and `Incisitermes`
- filter observations to the actual Alabama county polygons
- replace `iNaturalist_records.csv`
- update `external_data_snapshot.json`

To force a fresh county download:

```text
python update_external_data.py --refresh-counties
```

There is no GitHub Action for this workflow in Version 0.

## Website loading behavior

At startup, `index.html` loads these local repository files:

- `map_config.json`
- `AU-termite-samples.csv`
- `FSTrecords.csv`
- `alabama_counties.geojson`
- `external_data_snapshot.json`

`iNaturalist_records.csv` is not requested until the user turns on the iNaturalist layer.

`index.html` makes no live Census TIGERweb or iNaturalist API requests. External web requests are limited to the OpenStreetMap basemap tiles and the Leaflet/Papa Parse libraries.

## GitHub Pages

This repository can be published directly with GitHub Pages because `index.html` is in the repository root. Version 0 development is currently on `agent/version-0-map`; do not merge it to `main` until it has been reviewed.
