import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';
import 'package:gui/pages/user/add_sid_view.dart';
import 'package:gui/pages/user/dashboard_view.dart';
import 'package:gui/pages/user/logout_view.dart';
import 'package:gui/pages/user/notifications_view.dart';
import 'package:gui/pages/user/overview_view.dart';
import 'package:gui/pages/user/profile_view.dart';
import 'package:gui/pages/user/settings_view.dart';
import 'package:gui/pages/user/sid_view.dart';
import 'package:gui/pages/user/statistics_view.dart';
import 'package:gui/pages/user/user_overview.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    SideBarController sideBarController = Get.put(SideBarController());
    var pages = [
      DashboardPage(sideBarController: sideBarController),
      NotificationsPage(sideBarController: sideBarController),
      SatelliteDataPage(sideBarController: sideBarController),
      StatisticsPage(sideBarController: sideBarController),
      ProfilePage(sideBarController: sideBarController),
      SettingsPage(sideBarController: sideBarController),
      LogoutPage(),
      AddSidPage(sideBarController: sideBarController),
    ];
    sideBarController.pages = pages;

    DewsUser user = DewsUser(
      id: "test123",
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
