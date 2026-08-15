# AL-termite-map

Prototype of the Alabama Termite Map.

## Version 0

Version 0 is intentionally minimal. It reads `AU-termite-samples.xlsx` directly in the browser and displays the first 25 records that have usable coordinates within Alabama.

The current purpose is to verify the basic workflow:

1. Museum specimen data remain in the Excel workbook.
2. The web map reads those records.
3. Valid Alabama coordinates are plotted with Leaflet.
4. Clicking a point shows basic specimen metadata.

The prototype uses Leaflet, OpenStreetMap tiles, and SheetJS. There is no database or server-side application.

## Next steps

- Confirm which workbook columns should become the stable public data schema.
- Move data preparation from browser-side Excel parsing to an R script that produces GeoJSON.
- Add species-specific symbols or colors.
- Add the county-level published-record layer for *Coptotermes formosanus*.
- Add optional iNaturalist Research Grade records as a separate unverified layer.
