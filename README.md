# AL-termite-map

Prototype of the Alabama Termite Map.

## Version 0

Version 0 is a small static Leaflet map with no database or server-side application.

### Data

- `AU-termite-samples.csv`: verified AU voucher specimen records with coordinates.
- `FSTrecords.csv`: county-level records of *Coptotermes formosanus*, including first detected year.
- Alabama county boundaries: U.S. Census Bureau TIGERweb GeoJSON service.

### Current interface

The map currently focuses on three genera:

- *Coptotermes*
- *Reticulitermes*
- *Kalotermes*

Users can select a genus and independently show or hide:

- verified specimen points
- FST county records

The FST county layer is associated with *Coptotermes* and is displayed only when *Coptotermes* or all genera are selected.

Point colors represent genus. County shading represents documented county-level occurrence and should not be interpreted as occurrence throughout the county.

## Development direction

The current browser-side CSV workflow is intentionally simple. Later versions can move data preparation into R and generate derived GeoJSON while keeping the public site static and easy to maintain.

Potential next additions include species-level filtering within each genus and optional iNaturalist Research Grade observations as a separate unverified layer.
