import "package:firebase_database/firebase_database.dart";
import "package:gui/models/notification_model.dart";
import "package:gui/models/sid_model.dart";
import "package:gui/models/user_model.dart";

class FirebaseDatabaseUtils {
  static Future<int> createEntry(String path, dynamic data) async {
    try {
      await FirebaseDatabase.instance.ref().child(path).set(data);
      return 1;
    } catch (e) {
      // Error handling
      print("Create entry error: $e");
      return -1;
    }
  }

  static Future<int> appendToEntry(String path, dynamic data) async {
    final DatabaseReference ref = FirebaseDatabase.instance.ref().child(path);

    try {
      // Get current value
      final DatabaseEvent dbEvent = await ref.once();
      final currentVal = dbEvent.snapshot.value;

      List<dynamic> updatedArray;
      if (currentVal is List) {
        // If the current value is an array, append the data to it
        updatedArray = List.from(currentVal)..add(data);
      } else {
        updatedArray = [data];
      }

      // Set data
      await ref.set(updatedArray);

      return 1;
    } catch (e) {
      // Error handling
      print("Create entry error: $e");
      return -1;
    }
  }

  static Future<Map<String, dynamic>?> readEntry(String path) async {
    try {
      DataSnapshot dataSnapshot =
          (await FirebaseDatabase.instance.ref().child(path).once()).snapshot;
      return dataSnapshot.value as Map<String, dynamic>?;
    } catch (e) {
      // Error handling
      print("Read entry error: $e");
      return null;
    }
  }

  static Future<int> updateEntry(String path, Map<String, dynamic> data) async {
    try {
      await FirebaseDatabase.instance.ref().child(path).update(data);
    } catch (e) {
      // Error handling
      print("Create entry error: $e");
      return -1;
    }
    return 1;
  }

  /// Deletes entry in the database located at `path`.
  static Future<int> deleteEntry(String path) async {
    try {
      await FirebaseDatabase.instance.ref().child(path).remove();
    } catch (e) {
      // Error handling
      print("Create entry error: $e");
      return -1;
    }
    return 1;
  }

  /// Returns a list of all satellite image data models stored in the database.
  ///
  /// Return value: List<Map<String, SatelliteImageDataModel>>

  static Future<List<dynamic>> getSidEntries() async {
    try {
      DatabaseReference dbRef = FirebaseDatabase.instance.ref().child("sid");
      final dbEvent = await dbRef.once();
      Map<String, dynamic> satelliteTypesMap =
          dbEvent.snapshot.value as Map<String, dynamic>;
      List<SatelliteDataModel> entriesList = [];

      if (satelliteTypesMap.isNotEmpty) {
        satelliteTypesMap.forEach((satelliteType, sidMap) {
          sidMap.forEach((id, sidJson) {
            var sidModel = SatelliteDataModel.fromJson(sidJson);
            entriesList.add(sidModel);
            print("LENGTH (sid): ${entriesList.length}");
          });
        });
      } else {
        print("Database event's snapshot value is empty (sid).");
      }

      return entriesList;

      //
      // dbRef.once().then((DatabaseEvent dbEvent) {
      //   Map<String, dynamic> satelliteTypesMap =
      //       dbEvent.snapshot.value as Map<String, dynamic>;
      //   print("* * * * * * * * * *");
      //   print(satelliteTypesMap);
      //   print("* * * * * * * * * *");
      //   if (satelliteTypesMap.isNotEmpty) {
      //     satelliteTypesMap.forEach((satelliteType, sidMap) {
      //       print("# # # # # # # # # # # #");
      //       print(sidMap);
      //       print("# # # # # # # # # # # #");
      //       sidMap.forEach((id, sidJson) {
      //         print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~");
      //         print(sidJson);
      //         print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~");
      //         var sidModel = SatelliteImageDataModel.fromJson(sidJson);
      //         print("${sidModel.id} -~*");
      //         entriesList.add(sidModel);
      //         print("LENGTH: ${entriesList.length}");
      //       });
      //     });
      //   } else {
      //     print("Database event's snapshot value is empty.");
      //   }
      // });
    } catch (e) {
      // Error handling
      print("Could not get SID entries: $e");
      return [];
    }
    // print("jupp: ${entriesList.length}");
    // return [1, entriesList];
  }

  static DewsUser getUserById(String userId) {
    // TODO: implement real function
    return DewsUser(
      id: "kj23n4kj234n",
      // userGroups: ["admin"],
      email: "peter@web.de",
      firstName: "Peter",
      lastName: "Manfred",
      streetName: "Herrmann Straße",
      streetNumber: 81,
      postalCode: 98045,
      country: "Germany",
      phoneNumber: "016205738280",
      createdTimestamp: DateTime.now(),
      lastModifiedTimestamp: DateTime.now(),
      newFilesCount: 1,
      notificationsCount: 1,
    );
  }

  static Future<List<dynamic>> getNotificationEntries(String userId) async {
    List<dynamic> entriesList = [];
    try {
      DatabaseReference dbRef =
          FirebaseDatabase.instance.ref().child("notifications/$userId");
      final dbEvent = await dbRef.once();
      List<dynamic> notificationsList = dbEvent.snapshot.value as List<dynamic>;

      if (notificationsList.isNotEmpty) {
        for (var index = 0; index < notificationsList.length; index++) {
          var notificationModel = NotificationModel.fromJson(notificationsList[index]);
          entriesList.add(notificationModel);
        }
      } else {
        print("Database event's snapshot value is empty (notifications). userId='$userId'");
      }

      return entriesList;
    } catch (e) {
      // Error handling
      print("Could not get notification entries. userId='$userId', error='$e'");
      return entriesList;
    }
  }
}
