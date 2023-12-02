import os

# Project
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEBUG_STATUS = True
MAX_RETRIES = 20
THREAD_TIMEOUT = 180

# Flask API
FLASK_NAME = "dews"
FLASK_HOST = "0.0.0.0"  # locally
FLASK_PORT = 5000  # locally
MAX_CONTENT_LENGTH = 2000 * 1024 * 1024  # 2GB, 2000 MB

# Database
DB_HOST = "172.19.0.3"  # over network
DB_PORT = 5432  # over network
DB_NAME = "dews"
DB_USER = "dews"
DB_PASSWORD = "dews"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Logger
LOGGER_FILE_LOCATION = os.path.join(ROOT_PATH, "backend.log")
LOGGER_FILE_MODE = "w"  # 'w': create new log on every run; 'a': append to existing log
LOGGER_FORMAT = "[%(asctime)s] | %(levelname)s - %(module)s.%(funcName)s[%(lineno)d]: %(message)s"
LOGGER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_LEVEL = "DEBUG"

# Files
ROOT_FILES_PATH = os.path.join(ROOT_PATH, "files")
EXTRACTED_FILES_PATH = os.path.join(ROOT_FILES_PATH, "extracted")
ZIP_FILES_PATH = os.path.join(ROOT_FILES_PATH, "zip")
IMAGES_FILES_PATH = os.path.join(ROOT_FILES_PATH, "images")
OTHER_FILES_PATH = os.path.join(ROOT_FILES_PATH, "other")
FILES_PATH_LIST = [ROOT_FILES_PATH, EXTRACTED_FILES_PATH, ZIP_FILES_PATH,
                   IMAGES_FILES_PATH, OTHER_FILES_PATH]

# Sentinel-1A
S1A_DIRECTORY_STORAGE = "uploads/sentinel-1a"
S1A_MANIFEST_FILE_NAME = "manifest.safe"
# Sentinel-1B
S1B_DIRECTORY_STORAGE = "uploads/sentinel-1b"
# Sentinel-2A
S2A_DIRECTORY_STORAGE = "uploads/sentinel-2a"
# Sentinel-2B
S2B_DIRECTORY_STORAGE = "uploads/sentinel-2b"
S2B_METADATA_FILE_NAME = "MTD_MSIL2A.xml"
S2B_INSPIRE_FILE_NAME = "INSPIRE.xml"
S2B_IMG_FILE_EXTENSION = ".jp2"

# Landsat-1
LS1_UPLOAD_DIRECTORY = "uploads/landsat-1"
