import logging
import threading
from flask import Blueprint, request, jsonify
from backend.api.utils import ApiUtils
from backend.models.satellite_data.satellite_data import SatelliteData
from backend.database.firebase import FirebaseStorage
from backend.models.satellite_data.satellite_mission import SatelliteMission
from backend.models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData
from backend.config import *

uploads_api = Blueprint("uploads_api", __name__)


@uploads_api.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers",
                         "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods",
                         "GET, POST, PUT, DELETE, OPTIONS")
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
        request_json = request.get_json()["upload"]
    except Exception as e:
        err_msg = f"Request json data does not contain 'upload' key."
        logging.debug(err_msg)
        return jsonify(ApiUtils.create_err_msg(-1, err_msg, {"error_msg": e}))
    # Parse json
    storage_path = request_json["storage_path"]
    satellite_mission = request_json["satellite_mission"].lower()
    user_id = request_json["user_id"]
    area_name = request_json["area_name"]
    city = request_json["city"]
    postal_code = request_json["postal_code"]
    country = request_json["country"]

    # Download directory from storage
    local_path = FirebaseStorage.download_directory(
        storage_path, EXTRACTED_FILES_PATH)

    if local_path == "":
        # Local path is empty
        err_msg = f"Could not download '{storage_path}'. user_id='{user_id}', storage_path='{storage_path}', local_path='{local_path}', area_name='{area_name}'"
        logging.error(err_msg)
        # TODO: error code
        return jsonify(ApiUtils.create_err_msg(-1, err_msg)), 500
    else:
        # Create response json
        response_json = {"request":
                            {
                                "user_id": user_id,
                                "area_name": area_name,
                                "satellite_mission": satellite_mission,
                                "storage_path": storage_path,
                                "directory_path_local": local_path,
                                "city": city,
                                "postal_code": postal_code,
                                "country": country,
                            }
                        }
        
        # Check for valid satellite type
        if satellite_mission.lower() in [mission.value.lower() for mission in SatelliteMission]:
            try:
                # Create Sentinel-2B data object
                # Add local path to json
                request_json.update({"directory_path_local": local_path})
                # init_thread = threading.Thread(target=Sentinel2BData.init_from_json, args=(upload_json,))
                init_thread = threading.Thread(
                    target=SatelliteData.from_json, args=(request_json,))
                init_thread.start()
            except Exception as e:
                # Creation failure
                logging.error(
                    f"Failed to create SatelliteData object. error='{e}' user_id='{user_id}', satellite_mission='{satellite_mission}', local_path='{local_path}', area_name='{area_name}'")
                return jsonify(ApiUtils.create_err_msg(-1, f"Faield to create Sentinel-2B object: '{e}'", response_json)), 500

            # Creation success
            logging.debug(
                f"Creating SatelliteData object... user_id='{user_id}', satellite_mission='{satellite_mission}', area_name='{area_name}', storage_path='{storage_path}', local_path='{local_path}'")
            return jsonify(
                ApiUtils.create_success_msg(f"We will notify you via the client when we are done calculating the indexes.", response_json)), 200
        else:
            # Satellite type not supported
            err_msg = f"Satellite type '{satellite_mission}' not supported."
            logging.error(err_msg)
            # TODO: error code
            return jsonify(ApiUtils.create_err_msg(-1, err_msg, response_json)), 500
