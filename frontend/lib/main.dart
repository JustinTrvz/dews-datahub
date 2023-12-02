
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:gui/pages/side_bar/side_bar.dart';
import 'package:gui/pages/side_bar/side_bar_controller.dart';
import 'package:gui/pages/sid/add_sid_view.dart';
import 'package:gui/pages/logout_view.dart';
import 'package:gui/pages/notifications_view.dart';
import 'package:gui/pages/dashboard_view.dart';
import 'package:gui/pages/user/profile_view.dart';
import 'package:gui/pages/user/settings_view.dart';
import 'package:gui/pages/sid/sid_view.dart';
import 'package:gui/pages/statistics_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
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

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.orange,
      ),
      home: const SideNavBar(),
    );
  }
}
