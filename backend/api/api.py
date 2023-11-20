from flask import Flask, request, jsonify
from flask_cors import CORS
from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData
from database.firebase import FirebaseApp
from backend.config import *

import base64
import logging
import os

# Init Flask server
app = Flask(__name__)
CORS(app, resources={r"/sid*": {"origins": "http://127.0.0.1"}})
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Init Firebase app
database = FirebaseApp()


class DbErrorCodes:
    # Basic error codes
    NOT_IMPLEMENTED = -10000
    # Upload error codes
    NO_FILE_RECEIVED = -10010
    FILE_UPLOAD_FAILED = -10011
    WRONG_FILE_FORMAT = -10012
    SID_CREATION_ERR = -10013
    # Satellite image data
    SID_NOT_FOUND = -10020
    IMAGE_READ_ERR = -10030
    # User
    USER_CREATION_ERR = -10040
    USER_ALREADY_EXISTS = -10041


# Util functions
def create_err_msg(err_code: int, text: str):
    create_msg("error", err_code, text)


def create_success_msg(text):
    create_msg("Success", 1, text)


def create_msg(category: str, err_code: int, text: str):
    return {
        f"{category}": err_code,
        "text": text
    }


# Basic API functions
@app.route("/")
def home():
    response = {
        "info": "This is the 'Drought EWS' API."
    }
    return jsonify(response), 200


# Satellite Image Data
# TODO: create in backend's file system. do not upload! seperate data upload and creation process
@app.route("/sid/create/entry", methods=["POST"])
def create_sid_entry():
    # check attributes
    if request.form.get("postal_code") is None:
        postal_code = 0
    else:
        postal_code = request.form.get("postal_code")

    print(request.get_json())

    sid = Sentinel2BData(
        directory_path_local=os.path.join(
            ZIP_FILES_PATH, request.form.get("zip_file_name")),
        user_id=request.form.get("owner_id"),
        area_name=request.form.get("area_name"),
        country=request.form.get("country"),
        city=request.form.get("city"),
        postal_code=postal_code,
    )

    # add SatelliteImageData to database and check if successful
    ok = database.create_sid(sid_obj=sid)
    if ok <= 0:
        return jsonify(create_err_msg(
            DbErrorCodes.SID_CREATION_ERR,
            "Could not create a SatelliteImageData object in the database. Please try again!")), 500

    # in case everything went well, the ID will be returned
    return jsonify({"sid_id": sid.ID}), 201


@app.route("/sid/upload/zip2", methods=["POST"])
def upload_zip2():
    print("A")
    # Check if 'zip_file' exists
    if 'file' not in request.files:
        return jsonify(
            create_err_msg(DbErrorCodes.NO_FILE_RECEIVED,
                           "No file received. Request has no attribute 'file'.")), 400

    print("B")
    # Check if a file was selected
    zip_file = request.files["file"]
    if zip_file.filename == "":
        return jsonify(
            create_err_msg(DbErrorCodes.NO_FILE_RECEIVED,
                           "No file received, selected or empty file was send.")), 400

    print("C")
    try:
        print("Get content-range")
        content_range = request.headers.get('Content-Range')
        if content_range:
            print(f"Content-Range available: {content_range}")
            # Parse the content range header to get the start and end byte positions
            # "bytes 0-24999999/1147171584" -> "0-24999999/1147171584"
            content_range_string = content_range.split()[1]
            start_str, end_str, total_str = content_range_string.split('-')[0], \
                content_range_string.split(
                    '-')[1].split('/')[0], content_range_string.split('/')[1]

            start = int(start_str)
            end = int(end_str)
            total = int(total_str)
            print(f"Start: {start}, End: {end}, Total: {total}")

            # Check if the start byte is 0, indicating the first chunk
            zip_file_path = os.path.join(ZIP_FILES_PATH, zip_file.name)
            if start == 0:
                print("Create or open the file for writing")
                # Create or open the file for writing
                with open(zip_file_path, 'wb') as f:
                    f.write(request.data)
            else:
                print("Append the received chunk to the existing file")
                # Append the received chunk to the existing file
                with open(zip_file_path, 'ab') as f:
                    f.write(request.data)

            return jsonify(create_success_msg('Chunk received successfully')), 201
        else:
            return jsonify(
                create_err_msg(-1, 'Invalid request: Content-Range header is missing')), 400  # TODO: error code
    except Exception as e:
        print(str(e))
        return jsonify(create_err_msg(-2, str(e))), 500  # TODO: error code


@app.route("/sid/upload/zip1", methods=["POST"])
def upload_zip1():
    print(request.form.to_dict())
    print(request.headers.to_wsgi_list())
    print(request.files.to_dict())
    # Check if 'zip_file' exists
    if 'file' not in request.files:
        return jsonify(
            create_err_msg(DbErrorCodes.NO_FILE_RECEIVED,
                           "No file received. Request has no attribute 'file'.")), 400
    print("A")
    # Check if a file was selected
    zip_file = request.files["file"]
    if zip_file.filename == "":
        return jsonify(
            create_err_msg(DbErrorCodes.NO_FILE_RECEIVED,
                           "No file received, selected or empty file was send.")), 400

    print("B")
    headers = request.headers.to_wsgi_list()
    headers_dict = parse_headers(headers)
    chunk_index = 0
    chunk_byte_offset = 0
    total_chunk_count = 0
    total_file_size = 0
    # check if file successfully uploaded
    if zip_file:
        print("It is a file...")
        if ".zip" in zip_file.filename:
            print("It is a ZIP file!")
            zip_file_path = os.path.join(ZIP_FILES_PATH, zip_file.name)
            with open(zip_file_path, "ab") as destination:
                destination.seek(0, os.SEEK_END)
                destination.write(zip_file.stream.read())
        else:
            return jsonify(create_err_msg(
                DbErrorCodes.WRONG_FILE_FORMAT,
                "Wrong file format. Please upload a zip file that was provided by 'Copernicus Open Access Hub'!")), 400
    print("C")
    return jsonify(create_err_msg(
        DbErrorCodes.FILE_UPLOAD_FAILED,
        "Upload failed. Please try again!")), 400


@app.route('/sid/entries', methods=['GET'])
def get_entries():
    print(request.data)

    page = int(request.args.get('page', 1))  # Default to page 1
    page_size = int(request.args.get('page_size', 10))  # Default page size
    start = (page - 1) * page_size

    # Fetch entries from Firebase Realtime Database
    entries = database.SID_REF.order_by_key().limit_to_first(page_size).start_at(str(start)).get()

    return jsonify(entries)


def parse_headers(headers):
    headers_dict = {}


@app.route("/sid/edit/<sid_id>")
def edit_sid(sid_id):
    # TODO: complete method
    sid = database.get_sid(sid_id)
    return jsonify(
        {create_err_msg(DbErrorCodes.NOT_IMPLEMENTED, "Not implemented yet.")}), 403  # TODO: change error code


"""
@app.route("/sid/batch/")
def get_first_sid_batch():
    return get_sid_batch(0)



@app.route("/sid/batch/<page>")
def get_sid_batch(page=0):
    if page != "":
        page = int(page)
    start_index = 0
    end_index = 9
    if page >= 1:
        start_index = page * 10
        end_index = start_index + 10

    sid_amount = len(database.sid_list)
    print(f"SID_AMOUNT: {sid_amount}")
    if sid_amount == 0:
        return jsonify(create_err_msg(
            DbErrorCodes.SID_NOT_FOUND,
            f"No satellite image data available on the server. Number of satellite image data: {sid_amount}")), 204
    elif sid_amount >= 10:
        if sid_amount <= end_index:
            sid_list = database.sid_list[start_index:]
        else:
            sid_list = database.sid_list[start_index:end_index]
    else:
        sid_list = database.sid_list

    response = []
    for sid in sid_list:
        print(sid.ID)
        response.append(sid.to_dict())

    return jsonify(response)
"""


@app.route("/sid/get/<sid_id>")
def get_sid(sid_id):
    sid = database.get_sid(sid_id)

    if sid is None:
        return jsonify(
            create_err_msg(DbErrorCodes.SID_NOT_FOUND, f"Satellite image data with id '{sid_id}' not found.")), 404

    return jsonify(sid.to_dict()), 200


# Indexes
@app.route("/sid/get/ndvi/<sid_id>")
def get_ndvi(sid_id):
    img_path = ""
    sid_name = ""
    sid_owner = ""
    ndvi = ""
    base64_img = ""

    if img_path != "":
        try:
            with open(img_path, "rb") as img_file:
                base64_img = base64.b64encode(img_file.read()).decode("utf-8")
        except IOError:
            logging.error(
                f"Could not read image. img_path='{img_path}', http_code=500")
            return jsonify(
                create_err_msg(DbErrorCodes.IMAGE_READ_ERR,
                               f"Could not read image. img_path='{img_path}'")), 500  # TODO: change error code

    if ndvi != "" and base64_img != "":
        ndvi_response = {
            "sid_id": sid_id,
            "sid_name": sid_name,
            "sid_owner": sid_owner,
            "ndvi": ndvi,
            "ndvi_image": base64_img,
        }
    else:
        ndvi_response = {
            "info": f"Satellite image data has no calculated NDVI. sid_id='{sid_id}'"
        }

    logging.debug(f"Returned NDVI. sid_id='{sid_id}', sid_name='{sid_name}', sid_owner='{sid_owner}', "
                  f"ndvi='{ndvi}', img_path='{img_path}'")
    return jsonify(ndvi_response), 200


# User
@app.route("/user/create", methods=["POST"])
def create_user():
    # Get information from POST request
    data = request.get_json()
    user_nickname = data["user_nickname"]

    # Data base request: create user
    user_id = database.create_user(data)

    # Check if return value is numeric (error code)
    if isinstance(user_id, (int, float, complex)):
        if user_id == DbErrorCodes.USER_ALREADY_EXISTS:  # TODO: change error code
            err_msg = f"User name '{user_nickname}' already exists. error='{user_id}', user_name='{user_nickname}'"
            err_code = DbErrorCodes.USER_ALREADY_EXISTS
        else:
            err_msg = f"Creating user failed. error='{user_id}', user_name='{user_nickname}'"
            err_code = DbErrorCodes.USER_CREATION_ERR

        logging.error(err_msg)
        return jsonify(create_err_msg(err_code, err_msg)), 500
    else:
        logging.debug(
            f"Created a user. user_id='{user_id}', user_name='{user_nickname}'")
        return jsonify({"user_id": user_id, "user_nickname": user_nickname}), 201


if __name__ == "__main__":
    # Run flask server
    app.run(debug=DEBUG_STATUS)