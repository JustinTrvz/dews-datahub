import "package:firebase_database/firebase_database.dart";
import "package:gui/models/sid_model.dart";

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

  /// Returns a list of all satellite image data models stored in the database using this convention [int errorCode, List<Map<String, SatelliteImageDataModel>> entriesList].
  ///
  /// Please check the error code before using the sid list.
  static Future<List<dynamic>> getSidEntries() async {
    List<SatelliteImageDataModel> entriesList = [];
    try {
      DatabaseReference databaseReference =
          FirebaseDatabase.instance.ref().child("sid");
      databaseReference.once().then((DatabaseEvent dbEvent) {
        Map<String, dynamic> satelliteTypesMap =
            dbEvent.snapshot.value as Map<String, dynamic>;
        if (satelliteTypesMap.isNotEmpty) {
          satelliteTypesMap.forEach((satelliteType, sidMap) {
            sidMap.forEach((id, sidJson) {
              entriesList.add(SatelliteImageDataModel.fromJson(sidJson));
            });
          });
        } else {
          print("Database event's snapshot value is empty.");
        }
      });
    } catch (e) {
      // Error handling
      print("Could not get SID entries: $e");
      return [-1, entriesList];
    }
    return [1, entriesList];
  }
}
