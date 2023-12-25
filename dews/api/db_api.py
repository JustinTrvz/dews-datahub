from flask import Blueprint, jsonify
import logging

from backend.api.utils import ApiUtils
from backend.database.psql_client import PSQLClient as DbClient
from backend.api.err_codes import DbErrorCodes

db_api = Blueprint("db_api", __name__)


@db_api.route("/api/imgs/<sd_id>/<img_type>", methods=["GET"])
def get_img_info(sd_id: str, img_type: str):
    # Get image info object
    img_info = DbClient.get_img_info(sd_id, img_type)

    # Error handling
    if img_info is None:
        logging.error(f"Could not get image info item from database. sd_id='{sd_id}', img_type='{img_type}'")
        request = {"sd_id": sd_id, "img_type": img_type}
        return ApiUtils.create_err_msg(DbErrorCodes.IMG_READ_ERR, "Image not found.", request), 404

    # Return image info JSON
    return jsonify(img_info.to_dict()), 200


@db_api.route("/api/sd/<sd_id>", methods=["GET"])
def get_sd(sd_id: str):
    # Get satellite data object
    sd = DbClient.get_sd(sd_id)

    # Error handling
    if sd is None:
        logging.error(f"Could not get satellite data item from database. sd_id='{sd_id}'")
        request = {"sd_id": sd_id}
        return ApiUtils.create_err_msg(DbErrorCodes.SD_NOT_FOUND, "Satellite data not found.", request), 404

    # Return satellite data JSON
    return jsonify(sd.to_dict()), 200
