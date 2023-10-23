import logging
import threading
from firebase_admin import db
from backend.config import *
from backend.data.database.firebase import FirebaseApp, FirebaseStorage
from backend.data.models.satellite_data.satellite_types import SatelliteTypes
from backend.data.models.satellite_data.sentinel2b_data import Sentinel2BData


class UploadListener:
    @staticmethod
    def start():
        FirebaseApp.get_reference("uploads").listen(UploadListener.__listener)

    @staticmethod
    def __listener(event: db.Event):
        # Return if something was removed or nothing was uploaded
        if event.data is None:
            return

        logging.debug(
            f"New event '{event.event_type}' in path '{event.path}' with data '{event.data}'.")
        print(
            f"New event '{event.event_type}' in path '{event.path}' with data '{event.data}'.")

        # 'event.data' can be a list or a string
        if isinstance(event.data, str):
            if event.data == "":
                return
            dictionaries = [event.data]
        else:
            dictionaries = event.data

        # Delete uploads' array
        FirebaseApp.get_reference("uploads").delete()
        # print(uploads_arr)
        for dict in dictionaries:
            # Download directory
            user_id = dict["user_id"]
            upload_path = dict["upload_path"]
            area_name = dict["area_name"]
            postal_code = dict["postal_code"]
            city = dict["city"]
            country = dict["country"]
            satellite_type = dict["satellite_type"]

            local_path = FirebaseStorage.download_directory(upload_path, EXTRACTED_FILES_PATH)
            print(f"LOCAL_PATH: {local_path}")
            if local_path == "":
                logging.error(
                    f"Could not download '{upload_path}'. user_id='{user_id}', upload_path='{upload_path}', local_path='{local_path}', area_name='{area_name}'")
                # TODO: what to do next?!
                continue
            else:
                if satellite_type == SatelliteTypes.SENTINEL_2B:
                    logging.debug(f"Create Sentinel2BData object... user_id='{user_id}', local_path='{local_path}', area_name='{area_name}'")
                    threading.Thread(
                    target=Sentinel2BData(
                        directory_path_local=local_path,
                        user_id=user_id,
                        area_name=area_name,
                        city=city,
                        postal_code=postal_code,
                        country=country,
                    )
                )
                else:
                    logging.error(f"Satellite type '{satellite_type}' not supported. user_id='{user_id}', local_path='{local_path}', area_name='{area_name}'")