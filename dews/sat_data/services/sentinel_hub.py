from datetime import datetime
import logging
from os import getenv

from sentinelhub import (
    SHConfig,
    CRS,
    BBox,
    SentinelHubRequest,
    bbox_to_dimensions,
    DataCollection,
    MimeType,
)

logger = logging.getLogger("django")

def get_shconfig():
    config = SHConfig()
    config.sh_client_id=getenv("SH_CLIENT_ID")  # TODO: uncomment in production
    config.sh_client_secret=getenv("SH_CLIENT_SECRET")  # TODO: uncomment in production
    config.sh_base_url = 'https://services.sentinel-hub.com'
    config.sh_token_url = config.sh_base_url + '/oauth/token'

    config.save()
    return config


def get_evalscript(script_type: str, bands: list):
    # Capitalize each band string (["b02"] -> ["B02"])
    bands = [band_str.capitalize() for band_str in bands]

    if script_type.lower() == "tc":
        # Use double curly brackets for escaping them when using ".format()"
        result = """
                //VERSION=3

                function setup() {{
                    return {{
                        input: [{{
                            bands: {bands}
                        }}],
                        output: {{
                            bands: {bands_count}
                        }}
                    }};
                }}

                function evaluatePixel(sample) {{
                    return [{evaluate_pixel_bands}];
                }}
                """
        bands_str_format = str(bands).replace("'", '"').upper()  # Ensuring double quotes for JSON compatibility
        bands_count = len(bands)
        evaluate_pixel_bands_format = ', '.join([f'sample.{band.upper()}' for band in bands])

        # Replace place holder
        result = result.format(
            bands=bands_str_format,
            bands_count=bands_count,
            evaluate_pixel_bands=evaluate_pixel_bands_format
        )
        
    elif script_type.lower() == "ndvi":
        return
    
    print(result)
    return result



def get_response_types(mimetypes):
    result = []
    for mimetype in mimetypes:
        result.append(SentinelHubRequest.output_response("default", mimetype))

    return result


def request_sat_data(bbox: tuple, resolution: int, data_folder: str, data_collection, mimetypes: list,
                     bands: list, start_date: datetime, end_date: datetime, evalscript=None, evalscript_type="tc"):
    """
    bbox:               `tuple` with coordinates as floats in this order 'min_lon, min_lat, max_lon, max_lat' (e.g. `(5.866, 47.270, 15.041, 55.058)`)
    resolution:         resolution in meters (e.g. `60` is 60 meter per pixel)
    data_folder:        local save location for the output files
    data_collection:    satellite data collection (e.g. `DataCollection.SENTINEL2_L1C`)
    mimetypes:          response types as `list` of `MimeType` objects (e.g. `[MimeType.PNG, MimeType.TIFF]`)
    bands:              `list` with bands as string (e.g. `["B01", "B12]`)
    start_date:         start of time interval
    end_date:           end of time interval
    evalscript:         [OPTIONAL] custom eval script as multi line string 
    evalscript_type:    Default: true color ("tc"); use preset eval script like "tc" for true color (if `evalscript` is provided then `evalscript` will be used instead)
    """

    # Bounding box + size
    bbox_obj = BBox(bbox=bbox, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox_obj, resolution=resolution)

    logger.debug(f"Image shape at {resolution} m resolution: {size} pixels. bbox='{bbox}'")

    # Get eval script
    if not evalscript:
        evalscript = get_evalscript(evalscript_type, bands)

    # Create request
    request_true_color = SentinelHubRequest(
        data_folder=data_folder,
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=data_collection,
                time_interval=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
            )
        ],
        responses=get_response_types(mimetypes),
        bbox=bbox_obj,
        size=size,
        config=get_shconfig(),
    )

    # Submit request + get response
    request_true_color.get_data(save_data=True)
    logger.debug(f"Requesting sat data from Sentinel Hub done. bbox='{bbox}'")

    return request_true_color

# re = request_sat_data(bbox=(12.44693, 41.870072, 12.541001, 41.917096),
#             resolution=60,
#             data_folder="/media/jtrvz/chugchug/Git/drought-ews/dews/media/sentinel_hub",
#             data_collection=DataCollection.SENTINEL2_L1C,
#             mimetypes=[MimeType.PNG, MimeType.TIFF],
#             bands=["B02", "B03", "B04", "B08"],
#             start_date=datetime(2024, 1, 1),
#             end_date=datetime(2024, 1, 1),
#         )

# print(re)
# print()
# print("DL: ", re.get_download_list())
# print("FN: ", re.get_filename_list())
# print("UL: ", re.get_url_list())
# print("DLL: ", re.download_list)
# print("FL: ", re.folder_list)