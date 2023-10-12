
from backend.data.database.firebase import FirebaseDB
from backend.statistics.utils.file_utils import FileUtils


### --- Init process --- ###

fdb = FirebaseDB()
root_path = FileUtils()
FileUtils.create_file_directories(root_path)


### --- Procedure --- ###

# sid = SatelliteImageData(
#     zip_file_path="/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip",
#     calculate=False)

sid1 = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip"
sid2 = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230726T103629_N0509_R008_T32UNE_20230726T120759.zip"
vid = "/home/jtrvz/pCloudDrive/Medien/Videos/Dashcam/Justin_DameFaellt_.zip"

# response = fdb.upload_zip_file(sid1, "sid")
# response = fdb.get_band_img("S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937", 20, "B02")
response = fdb.upload_zip_from_path(vid)
print("Response: ", response)
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

fdb.clean_up()
