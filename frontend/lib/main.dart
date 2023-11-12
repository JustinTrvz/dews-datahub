import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:gui/firebase_options.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';
import 'package:gui/pages/user/add_sid_view.dart';
import 'package:gui/pages/user/logout_view.dart';
import 'package:gui/pages/user/notifications_view.dart';
import 'package:gui/pages/user/overview_view.dart';
import 'package:gui/pages/user/profile_view.dart';
import 'package:gui/pages/user/settings_view.dart';
import 'package:gui/pages/user/sid_view.dart';
import 'package:gui/pages/user/statistics_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  if (kDebugMode) {
    try {
      await FirebaseStorage.instance.useStorageEmulator("localhost", 9199);
      await FirebaseAuth.instance.useAuthEmulator("localhost", 9000);
      FirebaseDatabase.instance.useDatabaseEmulator("localhost", 9000);
      ("Using Firebase Emulator Suite...");
    } catch (e) {
      print("Can not use Firebase Emulator Suite. error='$e'");
    }
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    SideBarController sideBarController = Get.put(SideBarController());
    sideBarController.addPage("dashboard", DashboardPage(sideBarController: sideBarController));
    sideBarController.addPage("notifications", NotificationsPage(sideBarController: sideBarController));
    sideBarController.addPage("satellite-data", SatelliteDataPage(sideBarController: sideBarController));
    sideBarController.addPage("statistics", StatisticsPage(sideBarController: sideBarController));
    sideBarController.addPage("profile", ProfilePage(sideBarController: sideBarController));
    sideBarController.addPage("settings", SettingsPage(sideBarController: sideBarController));
    sideBarController.addPage("logout", LogoutPage());
    sideBarController.addPage("satellite-data/add", AddSidPage(sideBarController: sideBarController));

    DewsUser user = DewsUser(
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

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: SideNavBar(),
    );
  }
}
