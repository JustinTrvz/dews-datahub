import 'package:uuid/uuid.dart';

class NotificationModel {
  String notificationId;
  String userId;
  String category;
  String message;
  String? thumbnail;
  DateTime creationTime = DateTime.now();
  

  NotificationModel({
    this.notificationId = "Unknown",
    this.userId = "Unknown",
    this.category = "Unknown",
    this.message = "No message",
    this.thumbnail = "",
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    var jsonNotification = json["notification"];
    return NotificationModel(
      notificationId: jsonNotification["notification_id"] as String,
      userId: jsonNotification["user_id"] as String,
      category: jsonNotification["category"] as String,
      message:  jsonNotification["message"] as String,
      thumbnail: jsonNotification["thumbnail"] as String
    );
  }

}