import os

##### ----- PROJECT CONSTANTS ----- #####
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_YML_PATH = ROOT_PATH + "/config.yml"
DEBUG_STATUS = True

# Database
DB_URL = "http://127.0.0.1:9000/?ns=drought-ews" # Adjust this path!
DB_TOKEN_PATH = "" # Adjust this path!

# Storage
STORAGE_URL = "drought-ews.appspot.com" # Adjust this path!
STORAGE_TOKEN_PATH = "" # Adjust this path!

# Logger
LOGGER_FILE_LOCATION = "backend.log"
LOGGER_FORMAT = "[%(asctime)s] | %(levelname)s - %(module)s.%(funcName)s[%(lineno)d]: %(message)s"
LOGGER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_LEVEL = "DEBUG"

# Files
ROOT_FILES_PATH = "/home/jtrvz/Git/drought-ews/backend/tmp/files" # Adjust this path!
EXTRACTED_FILES_PATH = os.path.join(ROOT_FILES_PATH, "extracted")
ZIP_FILES_PATH = os.path.join(ROOT_FILES_PATH, "zip")
IMAGES_FILES_PATH = os.path.join(ROOT_FILES_PATH, "images")
OTHER_FILES_PATH = os.path.join(ROOT_FILES_PATH, "other")
FILES_PATH_LIST = [ROOT_FILES_PATH, EXTRACTED_FILES_PATH, ZIP_FILES_PATH,
                   IMAGES_FILES_PATH, OTHER_FILES_PATH]

# already implemented in "api/api.py"
# TODO: Leave it like it is or import error codes from here to api/api.py?
""" 
##### ----- ERROR CODES ----- ######
# ----- Database ----- #
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
"""
