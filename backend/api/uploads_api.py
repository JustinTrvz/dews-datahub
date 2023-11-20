import logging
import threading
from flask import Blueprint, request, jsonify
from backend.api.utils import ApiUtils
from database.firebase import FirebaseStorage
from models.satellite_data.satellite_types import SatelliteType
from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData
from config import *

uploads_api = Blueprint("uploads_api", __name__)

@uploads_api.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    return response

@uploads_api.route("/uploads/notify", methods=["POST", "OPTIONS"])
def uploadNotification():

    if request.method == "POST":
        logging.debug("Received a uploads notification!")
    elif request.method == "OPTIONS":
        return jsonify(success=True), 200

    print(" - - - ")
    print(f"Rquest.: {request.headers}")
    print(" . . . ")
    print(f"Rquest.data: {request.data}")
    print(" . . . ")
    print(f"Rquest.values: {request.values}")
    print(" . . . ")
    print(f"Rquest.authorization: {request.authorization}")
    print(" . . . ")
    print(f"Rquest.base_url: {request.base_url}")
    print(" - - - ")

    # Get upload data
    try:
        upload_json = request.get_json()["upload"]
    except Exception as e:
        err_msg = f"Request json data does not contain 'upload' key."
        logging.debug(err_msg)
        return jsonify(ApiUtils.create_err_msg(-1, err_msg, {"error_msg": e}))
    # Parse json
    upload_path = upload_json["upload_path"]
    satellite_type = upload_json["satellite_type"]
    user_id = upload_json["user_id"]
    area_name = upload_json["area_name"]
    city = upload_json["city"]
    postal_code = upload_json["postal_code"]
    country = upload_json["country"]

    # Download directory from storage
    local_path = FirebaseStorage.download_directory(
        upload_path, EXTRACTED_FILES_PATH)

    if local_path == "":
        # Local path is empty
        err_msg = f"Could not download '{upload_path}'. user_id='{user_id}', upload_path='{upload_path}', local_path='{local_path}', area_name='{area_name}'"
        logging.error(err_msg)
        # TODO: error code
        return jsonify(ApiUtils.create_err_msg(-1, err_msg)), 500
    else:
        # Create request json to respond
        request_json = {"request":
                        {"user_id": user_id, "area_name": area_name,
                         "satellite_type": satellite_type, "upload_path": upload_path,
                         "local_path": local_path, "city": city,
                         "postal_code": postal_code, "country": country}
                        }
        # Check for satellite type
        if satellite_type.lower() == SatelliteType.SENTINEL_2B.lower():
            try:
                # Create Sentinel-2B data object
                # add local path to json
                upload_json.update({"directory_path_local": local_path})
                init_thread = threading.Thread(
                    target=Sentinel2BData.init_from_json, args=(upload_json,))
                init_thread.start()
            except Exception as e:
                # Creation failure
                logging.error(f"Failed to create Sentinel2BData object. error='{e}' user_id='{user_id}', local_path='{local_path}', area_name='{area_name}'")
                return jsonify(ApiUtils.create_err_msg(-1, f"Faield to create Sentinel-2B object: '{e}'", request_json)), 500

            # Creation success
            logging.debug(
                f"Creating Sentinel2BData object... user_id='{user_id}', area_name='{area_name}', satellite_type='{satellite_type}', upload_path='{upload_path}', local_path='{local_path}'")
            return jsonify(
                ApiUtils.create_success_msg(f"We will notify you via the client when we are done calculating the indexes.", request_json)), 200
        else:
            # Satellite type not supported
            err_msg = f"Satellite type '{satellite_type}' not supported."
            logging.error(err_msg)
            # TODO: error code
            return jsonify(ApiUtils.create_err_msg(-1, err_msg, request_json)), 500
