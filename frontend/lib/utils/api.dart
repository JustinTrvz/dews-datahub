import "dart:convert";
import "package:gui/utils/string_extensions.dart";

import "package:http/http.dart" as http;

class ApiUtils {
  static Map<String, dynamic> createUploadJson(
      String uploadPath,
      String satelliteType,
      String userId,
      String areaName,
      String city,
      int postalCode,
      String country) {
    return {
      "upload": {
        // System input: Do not touch the following three parameters!
        "upload_path": uploadPath,
        "satellite_type": satelliteType,
        "user_id": userId,
        // User input: only user's input needs to be cleaned
        "area_name": areaName.toLowerCase().capitalize(),
        "city": city.toLowerCase().capitalize(),
        "postal_code": postalCode,
        "country": country.toLowerCase().capitalize(),
      },
    };
  }

  static Future<int> sendUploadNotification(Map<String, dynamic> data) async {
    // const String apiEndpoint = "http://127.0.0.1:5000/uploads/notify"; // local
    const String apiEndpoint = "http://172.19.0.2:5000/uploads/notify"; // docker

    try {
      String jsonBody = jsonEncode(data);
      final response = await http.post(
        Uri.parse(apiEndpoint),
        headers: <String, String>{
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: jsonBody,
      );

      if (response.statusCode == 200) {
        print(
            "JSON sent successfully. apiEndpoint='$apiEndpoint', data='$data'");
        return 1;
      } else {
        print(
            "Failed to send JSON. response.statusCode='${response.statusCode}'");
        print("Printing response's body. response.body='${response.body}'");
        return -1;
      }
    } on Exception catch (e) {
      print("Failed to send JSON: '$e'");
      return -1;
    }
  }
}
