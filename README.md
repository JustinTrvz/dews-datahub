# DEWS's DataHub (Drought Early Warning System's DataHub)
DEWS'S datahub was made to import satellite data archives downloaded from e.g. [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/) to have an overview over your downloaded satellite data archives as well as a PostGIS database to connect with other software.

The satellite mission, product type, thumbnail, etc. will be automatically recognized and displayed in a new entry in the [SatData overview tab](http://0.0.0.0/sat_data/overview/). When the archive contains satellite images that are raster compatible they will be converted into rasters and imported into the PostGIS database (*located at [0.0.0.0:5432](http://0.0.0.0:5432)*).

# Guide
This guide shows how to start the Docker containers locally, how to use the web app, gives information about the PostGIS database, how to use with QGIS and which satellite datasets are supported.

## Start Docker container
1. Install `Docker` using the [official installation guide](https://docs.docker.com/engine/install/).
2. Install `Docker Compose` using the [official installation guide](https://docs.docker.com/compose/install/).
3. *OPTIONAL:* Install `Docker BuildX`.
     - **Linux:** `apt install docker-buildx`
     - **MacOS:** `brew install docker-buildx` 
     - **Other OS:** [Docker BuildX installation guide](https://github.com/docker/buildx#installing).
     - **INFO:** *If you experience any issues while building the Docker containers please see this step as necessary!*
4. Start a terminal.
5. Change directory to the root of the project (_e.g. `cd  ~/Git/drought-ews`_).
6. Build the containers:
     - `docker-compose up -d --build`
     - **INFO:** *In case something went wrong please run `sudo rm -rf pgdata/` and try `docker-compose up -d --build --force-recreate`.*
7. If you already build the Docker containers just start them using this command:
     - `docker-compose up -d` 


## Import data
After the import is finished an entry will be displayed in the [SatData overview tab](http://0.0.0.0/sat_data/overview/) but if raster compatible images exist in the archive the processing can take quite a bit of time.<br>
Please be patient! The process cannot be sped up since the official PostGIS script `raster2pgsql` is used which is already optimized for this kind of import.

### Import using the web app
1. Open [http://0.0.0.0/](http://0.0.0.0/).
2. Login with the default credentials `dews:dews`.
3. Visit [http://0.0.0.0/sat_data/upload/](http://0.0.0.0/sat_data/upload/) or click on the `Upload Satellite Data` button.
4. Choose the satellite data ZIP archive you want to upload.
   
### Import using Docker
1. Copy your local archive into the DEWS container's filesystem:
     - `docker cp <archive_path> dews:/dews/media/sat_data/archive/`
     - **Example:** `docker cp S1A_IW_GRDH_1SDV_20231116T053343_20231116T053408_051238_062E4B_84CA.SAFE.zip dews:/dews/media/sat_data/archive/`
2. Import your data into the database.
     1. Log into the DEWS container. 
        - `docker exec -it dews /bin/bash`
     2. Import your archive using the Django admin command `importdata`. 
        - `python manage.py importdata <archive_path> -m <sat_mission>`
        - **Example:** `python manage.py importdata /dews/media/sat_data/archive/S1A_IW_GRDH_1SDV_20231116T053343_20231116T053408_051238_062E4B_84CA.SAFE.zip -m sentinel-1a`

## DataHub Web App
### Description
On the [datahub's upload page]([http](http://0.0.0.0/sat_data/upload/)) you can upload official satellite dataset archives that were downloaded from a [supported satellite data source](#supported-satellite-data-sources) (*e.g. Dataspace Copernicus*)

After you have downloaded a satellite dataset you can upload the ZIP archive and let the system process the data.

So far the system shows the following data:
   - Satellite mission
   - Product type
   - Product start time
   - Product stop time
   - Archive path in filesystem 
     - *e.g. `dews/media/sat_data/archive/<archive>`*
   - Extracted archive path 
     - *e.g. `/dews/media/sat_data/extracted/<mission>/<archive_name>`*
   - Metadata files `manifest.safe`, `MTD_*.xml`, `INSPIRE.xml` and/or `xfdumanifest.xml`
   - Thumbnail image (*if available*)
   - Indicies and index images
     - *e.g. NDVI, EVI, ...*
   - Band table names in PostGIS database
     - *e.g. `3ed72523-fa4c-447b-b5db-19020d17a7ce_b02_r10m`*

## PostGIS
### PostGIS database
- **Location:** [0.0.0.0:5432](http://0.0.0.0:5432)
- Imported archive's images will be imported as a raster in an own table.
  - The name consists of the sat data id, the band (*e.g. B04 which stands for the red band*) and the range (*meters per pixel*), if available.
  - **Example table name:** `<sat_data_id>_<band>` / `<sat_data_id>_<band>_<range>`

### PostGIS Admin UI
A PostGIS Admin container `dews-db-gui` is started parallel to have an overview over the database.
   - Visit [http://0.0.0.0:5050/](http://0.0.0.0:5050/) to see the [PostGIS Admin](http://0.0.0.0:5050/) overview.
   - Use `dews@dews.de:dews` as credentials.


## QGIS
### Import into QGIS
1. Visit the [SatData overview tab](http://0.0.0.0/sat_data/overview/).
2. Select an entry whose bands/raster you want to import.
3. Scroll down to `Band Tables`.
4. Choose the table containing the raster you want to import.
    - *e.g. `3ed72523-fa4c-447b-b5db-19020d17a7ce_b02_r10m`* 
6. Open QGIS.
7. Select `Layer` > `Add Layer` > `Add Raster Layer`.
8. Select `PostgreSQL` on the left side panel.
9. Add the `PostGIS` database.
    - **Database:** `dews`
    - **User:** `dews`
    - **Password:** `dews`  
10. You can use the `Search options` option in the bottom or search manually.   
    - **HINT:** All tables are located in the `public` schema!

## Satellite images
### Supported satellite data sources
#### Dataspace Copernicus
- **Link:** [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/)
  
| Satellite Type | Instrument | Data Level      | Archive Naming Convention             | Support Status | Additional Info                                                                    |
| -------------- | ---------- | --------------- | ------------------------------------- | -------------- | ---------------------------------------------------------------------------------- |
| Sentinel-1A    | C-SAR      | Level-0 RAW     | `S1A_IW_RAW_0SDV_(...).SAFE.zip`      | ✅              |                                                                                    |
|                |            | Level-1 SLC     | `S1A_IW_SLC__1SDV_(...).SAFE.zip`     | ✅              |                                                                                    |
|                |            | Level-1 GRD     | `S1A_S1A_IW_GRDH_1SDV_(...).SAFE.zip` | ✅              |                                                                                    |
|                |            | Level-1 GRD COG | `S1A_IW_GRDH_1SDV_(...).SAFE.zip`     | ✅              | `.dat` files                                                                        |
|                |            | Level-2 OCN     | `S1A_IW_OCN_2SDV_(...).SAFE.zip`      | ✅              | `.nc` files                                                                        |
| Sentinel-1B    |            |                 | ❓                                     | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |

| Satellite Type | Instrument | Data Level | Archive Naming Convention   | Support Status | Additional Info |
| -------------- | ---------- | ---------- | --------------------------- | -------------- | --------------- |
| Sentinel-2     | MSI L1C    |            | `S2B_MSIL1C_(...).SAFE.zip` | ✅              |                 |
|                | MSI L2A    |            | `S2B_MSIL2A_(...).SAFE.zip` | ✅              |                 |

| Satellite Type | Instrument | Data Level     | Archive Naming Convention        | Support Status | Additional Info                                                                    |
| -------------- | ---------- | -------------- | -------------------------------- | -------------- | ---------------------------------------------------------------------------------- |
| Sentinel-3     | OLCI       | Level-1 EFR    | `S3A_OL_1_EFR____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-1 ERR    | `S3A_OL_1_ERR____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 LFR    | `S3A_OL_2_LFR____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 LRR    | `S3A_OL_2_LRR____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 WFR    | `S3A_OL_2_WFR____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 WRR    | `S3A_OL_2_WRR____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                | SRAL       | Level-1 SRA    | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-1 SRA_A  | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-1 SRA_BS | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-2 LAN    | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-2 WAT    | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-2 LAN_HY | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-2 LAN_SI | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                |            | Level-2 LAN_LI | ❓                                | ❌              | No data found at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |
|                | SLSTR      | Level-1 RBT    | `S3A_SL_1_RBT____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 AOD    | `S3A_SL_2_AOD____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 FRP    | `S3A_SL_2_FRP____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 LST    | `S3A_SL_2_LST____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 WST    | `S3A_SL_2_WST____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                | SYNERGY    | Level-2 SY_AOD | `S3B_SY_2_AOD____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 SY_SYN | `S3B_SY_2_SYN____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 SY_V10 | `S3B_SY_2_V10____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 SY_VG1 | `S3B_SY_2_VG1____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |
|                |            | Level-2 SY_VGP | `S3B_SY_2_VGP____(...).SEN3.zip` | ✅              | `.nc` files                                                                        |

| Satellite Type | Instrument | Data Level | Archive Naming Convention | Support Status | Additional Info                                                                                        |
| -------------- | ---------- | ---------- | ------------------------- | -------------- | ------------------------------------------------------------------------------------------------------ |
| Sentinel-5P    |            |            | ❓                         | ❌              | Work in progress, but no priority yet because this satellite's main observation goal is air pollution. |

| Satellite Type | Instrument | Data Level | Archive Naming Convention | Support Status | Additional Info                                                                    |
| -------------- | ---------- | ---------- | ------------------------- | -------------- | ---------------------------------------------------------------------------------- |
| Sentinel-6     |            |            | ❓                         | ❌              | Not available at [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/). |



#### EarthExplorer
- **Link:** [EarthExplorer](https://earthexplorer.usgs.gov/)
- **Datasets:**
  - `Landsat 3` 
    - **Support status:** ❌ *(WIP)*
  - `Landsat 4` 
    - **Support status:** ❌ *(WIP)*
  - `Landsat 5` 
    - **Support status:** ❌ *(WIP)*
  - `Landsat 6` 
    - **Support status:** ❌ *(WIP)*
  - `Landsat 7` 
    - **Support status:** ❌ *(WIP)*
  - `Landsat 8` 
    - **Support status:** ❌ *(WIP)*

## Download satellite datasets manually
### Dataspace Copernicus
For a video tutorial see this [YouTube video](https://www.youtube.com/watch?v=sMax7wkUrlI).
1. Open [Dataspace Copernicus](https://dataspace.copernicus.eu/browser/).
2. Login with your account or register first.
3. Select the selection tool on the right side.
4. Select your desired area on the map.
5. Click on the top left on the burger menu to open the advanced search.
6. Fill out the "Sensing Period" (_e.g. 2023/07/01 - 2023/07/10_).
7. Leave "Ingestion Period" empty!
8. Select "Mission: Sentinel-2".
9. Select "Satellite Platform" with value "S2B_*".
10. Fill out "Cloud Cover" with the value "[0 TO 9.4]".
11. Click on the magnifier button.
12. Download any product that you want by clicking the download button.
