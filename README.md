# Alabama Termite Map

Static public map of documented termite records in Alabama.

## Version 0

Version 0 uses Leaflet in a single `index.html` file. There is no database or server-side application.

The public-facing taxa are:

- Formosan subterranean termite (*Coptotermes formosanus*)
- Native subterranean termites (*Reticulitermes* spp.)
- Dark southern drywood termite (*Kalotermes approximatus*)
- Southeastern drywood termite (*Incisitermes snyderi*)

The default view shows the Formosan subterranean termite, published county records, and verified museum records. The optional iNaturalist layer is off by default.

## Data sources

### Verified specimens

`AU-termite-samples.csv` is the **public, privacy-filtered** map input derived from the local museum master data associated with the Auburn University Natural History Museum / Alabama Termite Identification Service.

Privacy-sensitive Formosan subterranean termite records are generalized before publication. Their public coordinates are displaced by up to 300 m and displayed as a 300 m-radius location-uncertainty circle. The circle indicates uncertainty in the public location, not the biological extent of a colony or population.

### Published Formosan subterranean termite county records

`FSTrecords.csv` contains county-level first-detection records used in:

Hu, X. P. & Mizumoto, N. (2026, in press). *Four decades of inland invasion by Formosan subterranean termite in Alabama: expansion associated with transportation infrastructure.* Preprint: https://doi.org/10.32942/X21H4M

County shading indicates documented occurrence in a county. It should not be interpreted as occurrence throughout the county or as evidence of absence from unshaded counties.

### iNaturalist

Research Grade observations are retrieved live from the iNaturalist API only when the user enables the layer.

The map requests licensed observations only, displays observer and observation-license information when supplied by the API, and links each point back to the original iNaturalist observation. iNaturalist photographs are not reproduced by this website.

### Boundaries and basemap

- Alabama county boundaries: U.S. Census Bureau TIGERweb GeoJSON service.
- Basemap: OpenStreetMap through Leaflet.

## Privacy workflow

The exact-coordinate master file must remain local and must not be committed to this public repository.

Files:

- `AU-termite-samples-secret.csv`: local exact-coordinate master file; ignored by Git.
- `.privacy_salt`: local secret used to keep generalized coordinates stable between runs; ignored by Git.
- `AU-termite-samples.csv`: generated public map file; this is the file that is committed.
- `make_public_data.py`: privacy-processing script.
- `make_public_data.bat`: one-click Windows wrapper.

### First run on Windows

1. Pull/clone the repository so the current exact `AU-termite-samples.csv` is present locally.
2. Double-click `make_public_data.bat`.
3. On the first run, the script copies the current CSV to `AU-termite-samples-secret.csv` and creates `.privacy_salt`.
4. The script then replaces `AU-termite-samples.csv` with the public privacy-filtered version.
5. Commit and push only `AU-termite-samples.csv`.

For later updates, edit/replace `AU-termite-samples-secret.csv` with the current master data and double-click `make_public_data.bat` again. The same `.privacy_salt` keeps each voucher's generalized public position stable.

For Formosan subterranean termite records, the public-data script also removes `locality` and `city` text so address-like information is not exposed through the CSV.

## Website

This repository can be published directly with GitHub Pages because `index.html` is in the repository root.

After Version 0 is merged to `main`, open **Settings → Pages**, choose **Deploy from a branch**, select **main** and **/(root)**, then save.

The project-site address will be:

`https://mizumoto-lab.github.io/AL-termite-map/`
