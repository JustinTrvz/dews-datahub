import os

# Project
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_YML_PATH = os.path.join(ROOT_PATH, "config.yml")
DEBUG_STATUS = True
MAX_RETRIES = 20
THREAD_TIMEOUT = 180

# Flask API
MAX_CONTENT_LENGTH = 2000 * 1024 * 1024  # 2GB, 2000 MB

# Firebase
FB_TOKEN_PATH = "/home/jtrvz/Git/drought-ews/backend/drought-ews-dev.json"
FB_EMULATOR_URL = "http://localhost:8080"
RETRY_LIMIT = 5
## Database
DB_URL = "http://127.0.0.1:9000/?ns=drought-ews-dev"
DB_URL_DEV = "localhost:9000/?ns=drought-ews-dev"
## Storage
STORAGE_URL = "drought-ews-dev.appspot.com" # Adjust this path! => ATTENTION: Do not use 'http://' or 'http://'!
STORAGE_URL_DEV = "http://localhost:9199"

# Logger
LOGGER_FILE_LOCATION = os.path.join(ROOT_PATH, "backend.log")
LOGGER_FILE_MODE = "w" # 'w': create new log on every run; 'a': append to existing log
LOGGER_FORMAT = "[%(asctime)s] | %(levelname)s - %(module)s.%(funcName)s[%(lineno)d]: %(message)s"
LOGGER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_LEVEL = "DEBUG"

# Files
ROOT_FILES_PATH = os.path.join(ROOT_PATH, "tmp", "files") # Adjust this path!
EXTRACTED_FILES_PATH = os.path.join(ROOT_FILES_PATH, "extracted")
ZIP_FILES_PATH = os.path.join(ROOT_FILES_PATH, "zip")
IMAGES_FILES_PATH = os.path.join(ROOT_FILES_PATH, "images")
OTHER_FILES_PATH = os.path.join(ROOT_FILES_PATH, "other")
FILES_PATH_LIST = [ROOT_FILES_PATH, EXTRACTED_FILES_PATH, ZIP_FILES_PATH,
                   IMAGES_FILES_PATH, OTHER_FILES_PATH]


# Sentinel-2A
S2A_UPLOAD_DIRECTORY = "uploads/sentinel-2a"
# Sentinel-2B
S2B_UPLOAD_DIRECTORY = "uploads/sentinel-2b"
S2B_METADATA_FILE_NAME = "MTD_MSIL2A.xml"
S2B_INSPIRE_FILE_NAME = "INSPIRE.xml"
S2B_IMG_FILE_EXTENSION = ".jp2"

# Landsat-1
LS1_UPLOAD_DIRECTORY = "uploads/landsat-1"



