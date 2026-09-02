# Alabama Termite Map

Public map of documented termite records in Alabama.

[Free Alabama Termite Identification Service](https://mizumoto-lab.com/alabama-termites/)

[See this map in Google Maps](https://www.google.com/maps/d/u/0/viewer?mid=1uSdbm_Cdmq-PsQRbd5_UKiZPakRJ8Mg&ll=32.665379522285626%2C-84.98180665309259&z=8)

The map combines three sources of termite records:

- **AU termite specimens** identified by termite researchers at Auburn University
- **Published county records** for Formosan subterranean termite
- **iNaturalist Research Grade observations** from a periodically updated static snapshot

Published county records are historical county-level evidence. A county can therefore be shaded even when no preserved AU specimen is currently available from that county.

The map supports the free Alabama Termite Identification Service and the accumulation of reliable information on termite distributions in Alabama.

## Privacy

Exact coordinates for AU termite specimens are kept private. Public specimen coordinates are generalized by up to 300 m before publication, and exact locality information is not included in the public data file. County and family are retained as public fields.

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

This creates the privacy-filtered `AU-termite-samples.csv` used by the public map and three specimen-layer files used for Google My Maps.

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

The AU specimens are divided into three compact import files so each taxonomic group can be toggled independently:

- `google_my_maps_formosan.csv`: Formosan subterranean termite specimens
- `google_my_maps_native_subterranean.csv`: native subterranean termite specimens
- `google_my_maps_drywood.csv`: drywood termite specimens in Kalotermitidae

Each file contains only recognized Alabama records, with common and scientific names, privacy-generalized coordinates, date, county, family, AU ID, collector, identification details, and binary alate status. Import each file using the `Latitude` and `Longitude` columns and choose `Scientific name` as the marker title. The optional iNaturalist layer can be imported from `iNaturalist_records.csv` using its `lat` and `lon` columns.

## Main files

- `index.html`: map application
- `map_config.json`: taxa, colors, and display settings
- `map_text.json`: public-facing wording and references
- `AU-termite-samples.csv`: privacy-generalized AU specimen records
- `FSTrecords.csv`: published Formosan subterranean termite county records
- `google_my_maps_counties.csv`: Google My Maps import file for county-level records
- `google_my_maps_formosan.csv`: Google My Maps import file for Formosan subterranean termite specimens
- `google_my_maps_native_subterranean.csv`: Google My Maps import file for native subterranean termite specimens
- `google_my_maps_drywood.csv`: Google My Maps import file for drywood termite specimens
- `iNaturalist_records.csv`: static iNaturalist Research Grade snapshot
- `alabama_counties.geojson`: Alabama county boundaries
- `make_public_data.py`: creates the public specimen and Google My Maps datasets
- `update_external_data.py`: updates external map data

## Reference

Hu, X. P. & Mizumoto, N. (2026). *Four decades of inland invasion by the Formosan subterranean termite in Alabama: expansion associated with transportation infrastructure.* *Urban Ecosystems* 29, 244. https://doi.org/10.1007/s11252-026-02107-z

## Development

The map is a static HTML/JavaScript application using [Leaflet](https://leafletjs.com/), [Papa Parse](https://www.papaparse.com/), and OpenStreetMap/Esri basemap tiles.

Development of the web application and supporting scripts was assisted by ChatGPT (OpenAI).
