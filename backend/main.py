
import time
import uuid
from backend.data.database.db_listener import UploadListener
from backend.data.models.satellite_data.satellite_types import SatelliteTypes
from backend.data.models.satellite_data.sentinel2b_data import Sentinel2BData
from backend.data.models.user import User, UserGroups
from backend.statistics.utils.sid_logger import SidLogger
from data.database.firebase import *
from statistics.utils.file_utils import FileUtils
from config import *

### --- Init process --- ###
logger = SidLogger()

if DEBUG_STATUS:
    os.environ["FIRESTORE_EMULATOR_HOST"] = FB_EMULATOR_URL
    os.environ["FIREBASE_DATABASE_EMULATOR_HOST"] = DB_URL_DEV
    os.environ["STORAGE_EMULATOR_HOST"] = STORAGE_URL_DEV

### --- Firebase init --- ###
FileUtils.create_file_directories()
app = FirebaseApp.get_app()
UploadListener.start()

### --- Create satellite image  data --- ###
# sid = Sentinel2BData(
#     zip_file_path="/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip",
#     calculate=False)

sid1 = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip"
sid2 = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.SAFE"
vid = "/home/jtrvz/pCloudDrive/Medien/Videos/Dashcam/Eingesendet_LetsDashcam/Justin_DameFaellt_0.17.mov"

# Upload zip to Firebase Storage
response = FirebaseStorage.upload_directory(sid2, S2B_UPLOAD_DIRECTORY)
print(f"Response: {response}")
response = 1
if response >= 1:
    data_dict = {
        "upload_path": os.path.join(S2B_UPLOAD_DIRECTORY, FileUtils.extract_file_name(sid2)),
        "satellite_type": SatelliteTypes.SENTINEL_2B,
        "user_id": str(uuid.uuid4()),
        "area_name": "Bauernhof Manni",
        "city": "Dresden",
        "postal_code": 63754,
        "country": "Germany"
    }
    key = FirebaseDatabase.add_to_array("uploads", data_dict)
    print(f"Key: {key}")

# response = fdb.get_band_img("S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937", 20, "B02")
# response = fdb.upload_zip_from_path(vid)
# print("Response: ", response)
# response = fdb.upload_zip_from_path(sid2)
# print("Response: ", response)

# user = User(
#     name="Justin",
#     surname="Tran",
#     mail="jt@gmx.de",
#     street_name="Am Rollberg",
#     street_number=3,
#     postal_code=33567,
#     city="Swagburg",
#     country="Alnokkio")

# fdb.create_user(user_obj=user)
# users = fdb.get_user_batch()
# for id, user in users.items():
#     print(id, user)
#     break

# fdb.clean_up()
# exit(0)

# fdb.create_sdi(sid)
# fdb.get_sdi(sid.ID)

# user = User("ghjhjkhjk", "Justin", "Tran")
# fdb.create_user(user)


### --- Afterwards delete Firebase app --- ###

# fdb.clean_up()
