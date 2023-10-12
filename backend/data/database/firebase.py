import os
import zipfile

import firebase_admin
from firebase_admin import credentials, db, storage

from backend.statistics.utils.file_utils import FileUtils
from backend.data.models.satellite_image_data.sentinel2b_data import Sentinel2BData
from backend.models.user import User
from backend.config import *


class FirebaseDB:
    DEBUG = False
    FB_TOKEN = ""
    FB_APP_NAME = ""
    FB_APP = None

    # Database references
    SID_ROOT = None
    USER_ROOT = None

    # Storage references
    STORAGE_BUCKET = None

    def __init__(self, app_name: str = "[DEFAULT]"):

        # Set host to local Firebase Emulator Suite Storage
        if DEBUG_STATUS:
            os.environ["STORAGE_EMULATOR_HOST"] = "http://localhost:9199"

        # Create Firebase app
        try:
            self.FB_APP = firebase_admin.get_app(app_name)
        except ValueError:
            # If app does not exist, a value error is thrown
            if len(DB_TOKEN_PATH) > 0:
                # Production: Authentication token needed
                token = credentials.Certificate(DB_TOKEN_PATH)
                self.FB_APP = firebase_admin.initialize_app(
                    credential=token,
                    options={
                        "databaseURL": DB_URL,
                        "storageBucket": STORAGE_URL,
                    },
                    name=app_name,
                )
            else:
                # Development: No token needed using Firebase Emulator Suite
                self.FB_APP = firebase_admin.initialize_app(
                    options={
                        "databaseURL": DB_URL,
                        "storageBucket": STORAGE_URL,
                    },
                    name=app_name,
                )
        # References
        self.SID_ROOT = db.reference("sid")
        self.USER_ROOT = db.reference("user")
        # Firebase app specific
        self.FB_APP_NAME = app_name
        self.STORAGE_BUCKET = storage.bucket()

    def is_valid(self):
        if self.FB_TOKEN == "" or DB_URL == "" or \
                self.SID_ROOT is None or self.USER_ROOT is None or self.FB_APP is None:
            return False
        else:
            return True

    def create_sdi(self, sid_obj: Sentinel2BData) -> str:
        sid_ref = self.SID_ROOT.child(sid_obj.ID)
        sid_ref.set(sid_obj.to_dict())
        return sid_obj.ID

    def get_sdi(self, sid_id: str) -> Sentinel2BData | None:
        sid_ref = self.SID_ROOT.child(sid_id)
        sid_json = sid_ref.get()
        if sid_json:
            basic = sid_json.get("basic", {})
            files = sid_json.get("files", {})

            return Sentinel2BData(
                zip_file_path=files.get("zip_file_path"),
                owner_id=basic.get("owner_id"),
                area_name=basic.get("area_name"),
                country=basic.get("country"),
                city=basic.get("city"),
                postal_code=basic.get("postal_code"),
                calculate=False,
            )
        else:
            return None

    def get_band_img(self, folder_name, range, band):
        """
        Get the band image from captured satellite image data. You can find all images in the directory '.../GRANULE/[...]/IMG_DATA'.

        :param folder_name: Folder name (e.g. "S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937").
        :param range: Range in meters (e.g. 10, 20, 60).
        :param band: Band name (e.g. "AOT", "B02", "B04", "TCI").
        """

        # TODO: find a way to assemble the absolute path from the XML files (e.g. capture time)
        # Find info about naming convention!
        sid_blob = self.STORAGE_BUCKET.blob(
            f"sid/{folder_name}/{folder_name}.SAFE/GRANULE/L2A_T32UPE_A032595_20230603T103434/IMG_DATA/R{range}m/T32UPE_20230603T102559_{band}_{range}m.jp2")
        img_data = sid_blob.download_as_bytes()
        return img_data

    def get_sdi_batch(self) -> {}:
        # TODO: batching
        sid_dict = self.SID_ROOT.get()
        return sid_dict

    def get_user_batch(self) -> {}:
        # TODO: batching
        user_dict = self.USER_ROOT.get()
        return user_dict

    def upload_img_from_path(self, sid_id: str, img_path: str) -> str:
        # "test/img.jpeg" -> ["test", "img.jpeg"] -> "img.jpeg"
        img_name = img_path.split("/")[-1]
        # Get a reference to the Firebase Storage bucket
        sid_img_folder = self.STORAGE_BUCKET.blob(f"{sid_id}/{img_name}")
        sid_img_folder.upload_from_filename(filename=img_path)
        return sid_img_folder.public_url

    def upload_img_from_binary(self, sid_id: str, file_name: str, binary_img: str) -> str:
        # Get a reference to the Firebase Storage bucket
        sid_img_folder = self.STORAGE_BUCKET.blob(f"{sid_id}/{file_name}")
        sid_img_folder.upload_from_string(data=binary_img)
        return sid_img_folder.public_url

    def upload_zip_from_path(self, zip_path: str):
        # Set file name
        if "/" in zip_path:
            # "test/abc.zip" -> ["test", "abc.zip"] -> "abc.zip"
            zip_name = zip_path.split("/")[-1]
        else:
            zip_name = zip_path
        # Get a reference to the Firebase Storage bucket
        zip_folder = self.STORAGE_BUCKET.blob(f"zip/{zip_name}")
        zip_folder.upload_from_filename(zip_path)
        return zip_folder.public_url

    def upload_zip_from_api(self, file) -> str:
        sid_zip_folder = self.STORAGE_BUCKET.blob(f"zip/{file.filename}")
        sid_zip_folder.upload_from_file(file.stream)
        return sid_zip_folder.public_url

    def resumable_upload(self, file_path, chunk_size=25 * 1024 * 1024):
        # Set file name
        if "/" in file_path:
            # "test/abc.zip" -> ["test", "abc.zip"] -> "abc.zip"
            destination_blob_name = file_path.split("/")[-1]
        else:
            destination_blob_name = file_path

        # Get a reference to the Firebase Storage bucket
        bucket = storage.bucket()

        # Create a resumable upload session
        blob = bucket.blob(destination_blob_name)
        blob.chunk_size = chunk_size
        chunk_count = 0
        chunk_start = 0
        total_size = os.path.getsize(file_path)

        with open(file_path, 'rb') as file:
            while chunk_start < total_size:
                chunk_end = min(chunk_start + chunk_size, total_size)
                chunk_data = file.read(chunk_size)
                blob.upload_from_string(
                    chunk_data, content_type="application/zip")

                chunk_start = chunk_end
                chunk_count += 1
                print(
                    f'Uploaded chunk {chunk_count} / {total_size // chunk_size} ({chunk_start}/{total_size} bytes)')

        print('Resumable upload completed.')
        return blob.public_url

    def upload_zip_file(self, zip_path, storage_path) -> int:
        if not os.path.exists(zip_path):
            return -1  # TODO: ERROR CODE

        extracted_zip_path = self.extract_zip(zip_path)
        ok = self.upload_directory(extracted_zip_path, storage_path)

        return ok

    def extract_zip(self, zip_path):
        # Get the directory containing the zip file
        zip_dir = os.path.dirname(zip_path)

        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Determine the extraction path (use the zip file's name without extension)
            zip_base_name = os.path.splitext(os.path.basename(zip_path))[0]
            extraction_path = os.path.join(zip_dir, zip_base_name)

            # Extract the contents of the zip file to the extraction path
            zip_ref.extractall(extraction_path)

        return extraction_path

    def upload_directory(self, local_path, storage_path):
        # Set storage_path
        if "/" in local_path:
            # "test/abc.zip" -> ["test", "abc.zip"] -> "abc.zip"
            storage_path = f"{storage_path}/{local_path.split('/')[-1]}"
        else:
            storage_path = f"{storage_path}/{local_path}"

        for root, _, files in os.walk(local_path):
            for file_name in files:
                local_file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(local_file_path, local_path)
                destination_blob_name = os.path.join(
                    storage_path, relative_path)

                # Upload the file to Firebase Storage
                blob = self.STORAGE_BUCKET.blob(destination_blob_name)
                blob.upload_from_filename(local_file_path)

        return 1

    def create_user(self, user_obj: User) -> str:
        if user_obj.is_valid() is False:
            return ""

        user_ref = self.USER_ROOT.child(user_obj.ID)
        user_ref.set(user_obj.to_dict())
        return user_obj.ID

    def clean_up(self):
        firebase_admin.delete_app(self.FB_APP)
