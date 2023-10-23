import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

import 'package:gui/models/sid_model.dart';
import 'package:chunked_uploader/chunked_uploader.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';

class Database {
  Database();
  static Map<String, String> headersAcceptAll = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "*",
  };
  static Map<String, String> headersAcceptJson = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "*",
  };

  static String apiUrl = "http://127.0.0.1:5000";

  static Future<SatelliteImageDataModel> getSidById(String sidId) async {
    var uri = Uri.parse("$apiUrl/sid/get/$sidId");
    http.Response response = await http.get(
      uri,
      headers: headersAcceptAll,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> jsonData = json.decode(response.body);
      return SatelliteImageDataModel.fromJson(jsonData);
    } else {
      throw Exception(
          "Failed to load satellite image data model with id '$sidId'. (statusCode=${response.statusCode})");
    }
  }

  static Future<List<SatelliteImageDataModel>> getSidBatch() async {
    print("Get SID batches");
    var page = 1;
    var pageSize = 10;
    var requestUrl = "$apiUrl/sid/entries?page=$page&page_size=$pageSize";
    print(requestUrl);
    var uri = Uri.parse(requestUrl);
    http.Response response = await http.get(
      uri,
      headers: headersAcceptAll,
    );
    print("Request send...");
    print(response.statusCode);
    print("Body: ${response.body}");

    if (response.statusCode == 200) {
      print("TEEEEST");
      final List<dynamic> jsonReponse = json.decode(response.body);
      print("JSON RESPONSE: ${jsonReponse}");

      final List<SatelliteImageDataModel> sidList = jsonReponse.map((item) {
        return SatelliteImageDataModel.fromJson(item);
      }).toList();

      print("TEST");
      print(sidList);
      return sidList;
    } else if (response.statusCode == 204) {
      print("Empty list returned");
      return [];
    } else {
      throw Exception(
          "Failed to load satellite image data batch page '0'. (statusCode=${response.statusCode})");
    }
  }

  static Future<int?> uploadFile(PlatformFile file) async {
    try {
      final dio = Dio(BaseOptions(
        baseUrl: "$apiUrl/sid/upload/zip",
        headers: {
          "Accept": "application/json",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Access-Control-Allow-Origin": "*",
        },
      ));

      final uploader = ChunkedUploader(dio);
      final response = await uploader.uploadUsingFilePath(
        //fileDataStream: file.readStream!,
        fileName: file.name,
        //fileSize: file.size,
        maxChunkSize: 25000000, // bytes
        filePath: file.path!,
        path: "",
        onUploadProgress: (progress) => print("Progress: $progress"),
      );

      if (response == null) {
        return -1;
      } else {
        if (response.statusCode == 201) {
          print("File uploaded!");
        } else {
          print("Upload failed... ${response.statusCode}");
        }
        return response.statusCode;
      }
    } on Exception catch (e) {
      print("Exception: $e");
    }

    return -1;
  }

  static Future<int> createSidEntry(String zipFileName, String areaName,
      String city, String country, int postalCode) async {
    var uri = Uri.parse("$apiUrl/sid/create/entry");
    final jsonBody = {
      "zip_file_name": zipFileName,
      "owner_uuid": "abc123def456ghi789",
      "area_name": areaName,
      "country": country,
      "city": city,
      "postal_code": "$postalCode",
    };

    try {
      final response = await http.post(
        uri,
        body: jsonEncode(jsonBody),
        headers: {
          "Accept": "application/json",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Access-Control-Allow-Origin": "*",
        },
      );

      if (response.statusCode == 201) {
        print("SID entry attributes send to API!");
        print(response.body);
      } else {
        print("Sending failed... ${response.statusCode}");
        print(response.body);
      }
      return response.statusCode;
    } catch (e) {
      print("Error: $e");
      return -1;
    }
  }
}
