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