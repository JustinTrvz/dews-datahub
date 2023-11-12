import 'package:uuid/uuid.dart';

class NotificationModel {
  String id;
  String userId;
  String sidId;
  String category;
  String message;
  String? thumbnailStoragePath;
  DateTime creationTime = DateTime.now();
  

  NotificationModel({
    this.id = "Unknown",
    this.userId = "Unknown",
    this.sidId = "Unknown",
    this.category = "Unknown",
    this.message = "No message",
    this.thumbnailStoragePath = "",
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    var jsonNotification = json;
    return NotificationModel(
      id: jsonNotification["id"] as String,
      userId: jsonNotification["userId"] as String,
      sidId: jsonNotification["sidId"] as String,
      category: jsonNotification["category"] as String,
      message:  jsonNotification["message"] as String,
      thumbnailStoragePath: jsonNotification["thumbnailStoragePath"] as String
    );
  }

}