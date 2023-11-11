
import threading
import time
import uuid

from flask import Flask
from flask_cors import CORS
from backend.data.models.satellite_data.satellite_types import SatelliteTypes
from backend.data.models.satellite_data.sentinel2b_data import Sentinel2BData
from backend.data.models.user import User, UserGroups
from backend.statistics.utils.sid_logger import SidLogger
from data.database.firebase import *
from statistics.utils.file_utils import FileUtils
from config import *
from api.uploads_api import uploads_api
from api.basics_api import basics_api

app = Flask(__name__)
CORS(app)
app.register_blueprint(uploads_api)
app.register_blueprint(basics_api)


def run_flask_app():
    app.run(host=FLASK_HOST)

if __name__ == "__main__":
    # --- Create logger ---
    logger = SidLogger()
    print("Created logger...")

    # --- Flask API init (run as thread)
    try:
        threading.Thread(target=run_flask_app).start()
        print("Started Flask API server in thread...")
    except Exception as e:
        logging.error(
            f"Error occured while starting Flask API server in thread. error='{e}'")
    except KeyboardInterrupt as e:
        logging.error(
            f"Flask API server thread interrupted by keyboard input. error='{e}'")

    # --- Set environmental variables ---
    print(f"Debug status: {DEBUG_STATUS}")
    if DEBUG_STATUS:
        os.environ["FIRESTORE_EMULATOR_HOST"] = FB_EMULATOR_URL
        os.environ["FIREBASE_DATABASE_EMULATOR_HOST"] = DB_URL_DEV
        os.environ["STORAGE_EMULATOR_HOST"] = STORAGE_URL_DEV
        print("Set environmental variables...")


    # --- Firebase init ---
    FileUtils.create_file_directories()
    print("Created file directories...")
    app = FirebaseApp.init_app()
    print("Created Firebase app...")

    # --- Afterwards delete Firebase app --- ###
    # app.clean_up()
    # print("Deleted Firebase app...")
