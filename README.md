# Alabama Termite Map

Public map of documented termite records in Alabama.

[Free Alabama Termite Identification Service](https://mizumoto-lab.com/alabama-termites/)

The map combines three sources of termite records:

- **AU termite specimens** identified by termite researchers at Auburn University
- **Published county records** for Formosan subterranean termite
- **iNaturalist Research Grade observations** from a periodically updated static snapshot

Published county records are historical county-level evidence. A county can therefore be shaded even when no preserved AU specimen is currently available from that county.

The map supports the free Alabama Termite Identification Service and the accumulation of reliable information on termite distributions in Alabama.

## Privacy

Exact coordinates for AU termite specimens are kept private. Public specimen coordinates are generalized by up to 300 m before publication, and exact locality information is not included in the public data file.

The private files are:

```text
AU-termite-samples-secret.csv
.privacy_salt
```

These files must remain local and must never be committed.

To regenerate the public specimen file on Windows:

```text
make_public_data.bat
```

This creates the privacy-filtered `AU-termite-samples.csv` used by the public map.

## Updating external data

To update the iNaturalist snapshot and county-boundary data:

```text
update_external_data.bat
```

or:

```text
python update_external_data.py
```

Normal website visitors do not query the iNaturalist API directly. The map uses the static `iNaturalist_records.csv` snapshot stored in this repository.

## Google My Maps

`google_my_maps_counties.csv` is a convenience import file for the published Formosan county records. Its `Location` column uses county names such as `Mobile County, Alabama` so Google My Maps can place the county-level records without treating them as specimen coordinates. The marker location is only a county reference and is not a collection point.

`google_my_maps_AU_sample.csv` is the convenience import file for AU specimens. It contains only Alabama records recognized by the map and adds `scientific_name` and `common_name` columns while retaining the separate `genus` and `species` fields. Import it using the `lat` and `lon` columns; use `scientific_name` or `common_name` as the marker title or styling field. The optional iNaturalist layer can be imported from `iNaturalist_records.csv` using its `lat` and `lon` columns.

## Main files

- `index.html`: map application
- `map_config.json`: taxa, colors, and display settings
- `map_text.json`: public-facing wording and references
- `AU-termite-samples.csv`: privacy-generalized AU specimen records
- `FSTrecords.csv`: published Formosan subterranean termite county records
- `google_my_maps_counties.csv`: Google My Maps import file for county-level records
- `google_my_maps_AU_sample.csv`: Google My Maps import file for Alabama AU specimen records
- `iNaturalist_records.csv`: static iNaturalist Research Grade snapshot
- `alabama_counties.geojson`: Alabama county boundaries
- `make_public_data.py`: creates the public specimen dataset
- `update_external_data.py`: updates external map data

## Reference

Hu, X. P. & Mizumoto, N. (2026). *Four decades of inland invasion by the Formosan subterranean termite in Alabama: expansion associated with transportation infrastructure.* *Urban Ecosystems* 29, 244. https://doi.org/10.1007/s11252-026-02107-z

## Development

The map is a static HTML/JavaScript application using [Leaflet](https://leafletjs.com/), [Papa Parse](https://www.papaparse.com/), and OpenStreetMap/Esri basemap tiles.

Development of the web application and supporting scripts was assisted by ChatGPT (OpenAI).
