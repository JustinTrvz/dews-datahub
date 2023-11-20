import logging
import os

import firebase_admin
from firebase_admin import credentials, db, storage
from backend.statistics.utils.file_utils import FileUtils

from backend.data.models.user.user import User
from backend.config import *


class FirebaseApp:
    @staticmethod
    def init_app() -> firebase_admin.App:
        try:
            return firebase_admin.initialize_app(
                credentials.Certificate(FB_TOKEN_PATH),
                options={
                    "databaseURL": DB_URL,
                    "storageBucket": STORAGE_URL,
                })
        except Exception as e:
            logging.error(
                f"Firebase app was not initialized. Abort program. Please try again! error='{e}', DB_URL='{DB_URL}', STORAGE_URL='{STORAGE_URL}'")
            return None

    @staticmethod
    def get_reference(path: str):
        app = firebase_admin.get_app(name='[DEFAULT]')
        return db.reference(path=f"/{path}", app=app)

    @staticmethod
    def get_bucket():
        app = firebase_admin.get_app(name='[DEFAULT]')
        return storage.bucket(app=app)

    @staticmethod
    def clean_up():
        app = firebase_admin.get_app(name='[DEFAULT]')
        try:
            firebase_admin.delete_app(app=app)
            logging.debug(f"Deleted Firebase app '{app.name}'.")
        except Exception as e:
            logging.error(
                f"Could not delete Firebase app. Maybe the app is not initialized. error='{e}'")


class FirebaseDatabase:
    @staticmethod
    def entry_exists(reference: str):
        data = FirebaseApp.get_reference(reference).get()
        if data:
            return data, True
        else:
            return data, False

    @staticmethod
    def set_entry(reference: str, data):
        _, exists = FirebaseDatabase.entry_exists(reference)
        if exists:
            logging.debug(
                f"Reference '{reference}' already exists. Trying to push to entry...")
            ok = FirebaseDatabase.push_to_entry(reference, data)
            return (ok is not None)

        ref = FirebaseApp.get_reference(reference)
        try:
            ref.set(data)
        except Exception as e:
            logging.error(
                f"Could not set data to database reference '{reference}'. error='{e}', data='{data}'")
            return False
        return True

    @staticmethod
    def push_to_entry(reference: str, data):
        _, exists = FirebaseDatabase.entry_exists(reference)
        if not exists:
            logging.error(
                f"Could not push data to entry. Entry with reference '{reference}' does not exist!")
            return FirebaseDatabase.set_entry(reference, data)

        ref = FirebaseApp.get_reference(reference)
        logging.debug(f"Got data. reference='{reference}'")
        try:
            data_ref = ref.push(data)
            key = data_ref.key
            logging.debug(f"Pushed data to reference '{reference}'.")
        except Exception as e:
            logging.error(
                f"Could not push data to database reference '{reference}'. error='{e}', data='{data}'")
            return
        return key

    @staticmethod
    def add_to_array(reference: str, data):
        ref = FirebaseApp.get_reference(reference)
        existing_arr, exists = FirebaseDatabase.entry_exists(reference)

        if exists:
            if isinstance(existing_arr, list):
                existing_arr.append(data)
                try:
                    ref.set(existing_arr)
                    logging.debug(
                        f"Appended data to existing array. reference='{reference}'")
                except Exception as e:
                    logging.error(
                        f"Could not append data to existing array. error='{e}', reference='{reference}', data='{data}'")
                    return -1
            else:
                logging.error(
                    f"Can not add to array. Data at reference '{reference}' is not of type 'list'.")
                return -1
        else:
            try:
                ref.set([data])
                logging.debug(
                    f"Created and pushed array with data. reference='{reference}'")
            except Exception as e:
                logging.error(
                    f"Could create array with data. error='{e}', reference='{reference}', data='{data}'")
                return -1

        return 1

    @staticmethod
    def update_field(reference: str, field: str, data):
        _, exists = FirebaseDatabase.entry_exists(reference)
        if not exists:
            logging.error(
                f"Could not push data to entry. Entry with reference '{reference}' does not exist!")
            return False

        ref = FirebaseApp.get_reference(reference)
        try:
            ref.update({field: data})
            logging.debug(
                f"Updated field. reference='{reference}', field='{field}'.")
        except Exception as e:
            logging.error(
                f"Could not update field. reference='{reference}', field='{field}'. error='{e}', data='{data}'")
            return False
        return True

    @staticmethod
    def get_entry(reference: str, entry: str):
        _, exists = FirebaseDatabase.entry_exists(reference)
        if not exists:
            logging.error(
                f"Could not get entry. Entry with reference '{reference}' does not exist!")
            return

        ref = FirebaseApp.get_reference(reference)
        try:
            val = ref.child(entry).get()
            logging.debug(
                f"Got entry. reference='{reference}', entry='{entry}'")
        except Exception as e:
            logging.error(
                f"Value not available at database reference '{reference}/{entry}'. error='{e}'")
            return None
        return val

    """     
    @staticmethod
    def create_sid(sid_obj: Sentinel2BData) -> str:
        sid_ref = FirebaseApp.get_reference("sid").child(sid_obj.ID)
        sid_ref.set(sid_obj.to_dict())
        return sid_obj.ID

    @staticmethod
    def get_sid(sid_id: str) -> Sentinel2BData | None:
        sid_ref = FirebaseApp.get_reference("sid").child(sid_id)
        sid_json = sid_ref.get()
        if sid_json:
            basic = sid_json.get("basic", {})
            files = sid_json.get("files", {})

            return Sentinel2BData(
                directory_path=files.get("zip_file_path"),
                owner_id=basic.get("owner_id"),
                area_name=basic.get("area_name"),
                country=basic.get("country"),
                city=basic.get("city"),
                postal_code=basic.get("postal_code"),
                calculate=False,
            )
        else:
            return None
    """

    @staticmethod
    def get_entries():
        return FirebaseApp.get_reference("sid").get()

    @staticmethod
    def get_band_img(folder_name, range, band):
        """
        Get the band image from captured satellite image data. You can find all images in the directory '.../GRANULE/[...]/IMG_DATA'.

        :param folder_name: Folder name (e.g. "S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937").
        :param range: Range in meters (e.g. 10, 20, 60).
        :param band: Band name (e.g. "AOT", "B02", "B04", "TCI").
        """

        # TODO: find a way to assemble the absolute path from the XML files (e.g. capture time)
        # Find info about naming convention!
        sid_blob = FirebaseApp.get_bucket().blob(
            f"sid/{folder_name}/{folder_name}.SAFE/GRANULE/L2A_T32UPE_A032595_20230603T103434/IMG_DATA/R{range}m/T32UPE_20230603T102559_{band}_{range}m.jp2")
        img_data = sid_blob.download_as_bytes()
        return img_data

    @staticmethod
    def get_sdi_batch() -> {}:
        # TODO: batching
        sid_dict = FirebaseApp.get_reference("sid").get()
        return sid_dict

    @staticmethod
    def create_user(user_obj: User) -> str:
        if user_obj.is_valid() is False:
            return ""

        user_ref = FirebaseApp.get_reference("user").child(user_obj.ID)
        user_ref.set(user_obj.to_dict())
        return user_obj.ID

    @staticmethod
    def get_user_batch() -> {}:
        # TODO: batching
        user_dict = FirebaseApp.get_reference("user").get()
        return user_dict


class FirebaseStorage:
    @staticmethod
    def upload_file(destination_path: str, file_path: str) -> str:
        '''
        Writes file from "file_path" to "destination_path" in the Firebase Storage.

        E.g. upload_file("test/123", "/home/user/Downloads/file.zip") will write the file "file.zip" to "test/123/file.zip".
        '''
        # "test/img.jpeg" -> ["test", "img.jpeg"] -> "img.jpeg"
        img_name = file_path.split("/")[-1]
        # Get a reference to the Firebase Storage bucket
        blob_destination = f"{destination_path}/{img_name}"
        try:
            sid_img_folder = FirebaseApp.get_bucket().blob(blob_destination)
            sid_img_folder.upload_from_filename(filename=file_path)
        except Exception as e:
            logging.error(
                f"Failed to upload from file name. error='{e}', destination_path='{destination_path}', file_path='{file_path}', blob_destination='{blob_destination}'")
            print(f"Failed to upload from file name. error='{e}', destination_path='{destination_path}', file_path='{file_path}', blob_destination='{blob_destination}'")
            return ""

        return blob_destination

    @staticmethod
    def upload_file_bin(destination_path: str, file_name: str, img_bin: str) -> str:
        '''
        Writes binary to "destination_path" in the Firebase Storage.

        E.g. upload_file_bin("test/123", "file.zip", "z4R3bYx2Bnj3A") will write the file "file.zip" to "test/123/file.zip".
        '''
        # Get a reference to the Firebase Storage bucket
        sid_img_folder = FirebaseApp.get_bucket().blob(
            f"{destination_path}/{file_name}")
        sid_img_folder.upload_from_string(data=img_bin)
        return sid_img_folder.public_url

    @staticmethod
    def upload_zip_from_path(zip_path: str):
        # Set file name
        if "/" in zip_path:
            # "test/abc.zip" -> ["test", "abc.zip"] -> "abc.zip"
            zip_name = zip_path.split("/")[-1]
        else:
            zip_name = zip_path
        # Get a reference to the Firebase Storage bucket
        zip_folder = FirebaseApp.get_bucket().blob(f"zip/{zip_name}")
        zip_folder.upload_from_filename(zip_path)
        return zip_folder.public_url

    @staticmethod
    def extract_and_upload_zip(zip_path: str, storage_path: str) -> int:
        '''
        Extracts zip file and uploads the directory to the Firebase Storage.
        '''
        if not os.path.exists(zip_path):
            return -1  # TODO: ERROR CODE

        extracted_zip_path = FileUtils.extract_zip(zip_path)
        ok = FirebaseStorage.upload_directory(extracted_zip_path, storage_path)

        return ok
    
    @staticmethod
    def file_exists(reference: str, file_name: str) -> bool:
        try:
            blob = FirebaseApp.get_bucket().blob(f"{reference}/{file_name}")
            return blob.exists()
        except Exception as e:
            logging.error(f"Could not check if file exists. error='{e}', reference='{reference}', file_name='{file_name}'")
            return False

    @staticmethod
    def download_file(file_path: str, counter: int = 0) -> str:
        # Handle retries
        if counter >= RETRY_LIMIT:
            logging.error(
                f"Exceeded retry limit of {RETRY_LIMIT} with file '{file_path}'.")
            return
        elif counter >= 1:
            logging.debug(f"Retrying to download file '{file_path}'.")

        # Download file
        file_name = FileUtils.extract_file_name(file_path)
        blob = FirebaseApp.get_bucket().blob(file_path)
        destination_path = os.path.join(ZIP_FILES_PATH, file_name)
        try:
            blob.download_to_filename(destination_path)
        except Exception as e:
            logging.error(f"File '{file_path}' not found. error='{e}'")
            print(f"File '{file_path}' not found. error='{e}'")
            return ""
        # Error handling
        if os.path.exists(destination_path):
            logging.debug(
                f"Downloaded file '{file_name}' to '{destination_path}'.")
            print(f"Downloaded file '{file_name}' to '{destination_path}'.")
            return destination_path
        else:
            logging.error(
                f"Failed to download file '{file_name}' to '{destination_path}'.")
            return FirebaseStorage.download_file(file_path=file_path, counter=counter+1)

    @staticmethod
    def upload_directory(local_path, storage_path):
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
                try:
                    blob = FirebaseApp.get_bucket().blob(destination_blob_name)
                    blob.upload_from_filename(local_file_path)
                except Exception as e:
                    logging.error(
                        f"Could not upload file '{file_name} to storage path'{storage_path}. error='{e}'")
                    return 0
        logging.debug(
            f"Uploaded local directory '{local_path}' to storage '{storage_path}'.")
        print(
            f"Uploaded local directory '{local_path}' to storage '{storage_path}'.")
        return 1

    @staticmethod
    def download_directory(storage_path: str, local_path: str):
        '''
        Returns local directory's root path on success and an empty string on failure.
        '''
        # Check if local directory exists
        splitted_storage_path = storage_path.split('/')
        satellite_type = splitted_storage_path[-2]
        directory_name = splitted_storage_path[-1]
        full_local_path = f"{local_path}/{satellite_type}/{directory_name}"
        if os.path.exists(full_local_path):
            logging.debug(
                f"Local directory already exists. Will not download directory. full_local_path='{full_local_path}'")
            return full_local_path

        logging.debug(
            f"Local directory does not exist. About to download the remote directory. full_local_path='{full_local_path}', storage_path='{storage_path}'")
        blobs = FirebaseApp.get_bucket().list_blobs(prefix=storage_path)

        for blob in blobs:
            # Extract blob name
            path_components = blob.name.split("/")
            path_components.pop(0)  # Remove the first component ('uploads')

            # Generate local file path
            local_file_path = os.path.join(local_path, *path_components)

            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download the file to the local directory
            try:
                blob.download_to_filename(local_file_path)
            except Exception as e:
                logging.error(
                    f"Could not download file '{blob.name}' from Storage. error='{e}'")
                return ""

        # Extract the directory name from the storage path
        components = storage_path.split("/")
        components.pop(0)  # remove "uploads/" part
        local_dir_path = "/".join(components)
        print(f"local_dir_path: {local_dir_path}")

        return os.path.join(EXTRACTED_FILES_PATH, local_dir_path)

    @staticmethod
    def delete_directory(storage_path: str):
        blobs = list(FirebaseApp.get_bucket().list_blobs(prefix=storage_path))
        for blob in blobs:
            try:
                blob.delete()
            except Exception as e:
                logging.error(
                    f"Could not delete file '{blob.name} in Firebase Storage. error='{e}''")
                return 0
        logging.debug(f"Deleted directory '{storage_path}' from Storage.")
        print(f"Deleted directory '{storage_path}' from Storage.")
        return 1
