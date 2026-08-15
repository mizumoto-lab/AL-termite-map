# Alabama Termite Map

Static public map of documented termite records in Alabama.

## Version 0

Version 0 uses Leaflet in a single `index.html` file. There is no database or server-side application.

The public-facing taxa are:

- Formosan subterranean termite (*Coptotermes formosanus*)
- Native subterranean termites (*Reticulitermes* spp.)
- Dark southern drywood termite (*Kalotermes approximatus*)
- Southeastern drywood termite (*Incisitermes snyderi*)

The default view shows the Formosan subterranean termite, published county records, and verified specimen points. The optional iNaturalist layer is off by default.

## Data sources

### Verified specimens

`AU-termite-samples.csv` contains georeferenced voucher specimen records associated with the Auburn University Natural History Museum / Alabama Termite Identification Service.

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

## Website

This repository can be published directly with GitHub Pages because `index.html` is in the repository root.

After the Version 0 branch is merged to `main`, open **Settings → Pages**, choose **Deploy from a branch**, select **main** and **/(root)**, then save.

The default project-site address will be:

`https://nobuaki-mzmt.github.io/AL-termite-map/`

GitHub Pages publication from a private repository requires a GitHub plan that supports Pages for private repositories. Otherwise, the repository can be made public before enabling Pages.
