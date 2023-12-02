import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:gui/pages/side_bar/side_bar_controller.dart';

class SideNavBar extends StatefulWidget {
  const SideNavBar({Key? key}) : super(key: key);

  @override
  State<SideNavBar> createState() => _SideNavBarState();
}

class _SideNavBarState extends State<SideNavBar> {
  bool isExpanded = true;
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    SideBarController sideBarController = Get.put(SideBarController());

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon
            Icon(Icons.satellite),
            // Gap
            SizedBox(
              width: 5,
            ),
            Text(
              "DEWS's DataHub",
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.black,
        leadingWidth: 100,
        leading: GestureDetector(
          onTap: () {
            setState(() {
              isExpanded = !isExpanded;
            });
          },
          child: isExpanded
              ? const Row(
                  children: [
                    SizedBox(width: 25),
                    Icon(Icons.menu),
                    Icon(Icons.keyboard_arrow_left),
                  ],
                )
              : const Row(
                  children: [
                    SizedBox(width: 25),
                    Icon(Icons.menu),
                    Icon(Icons.keyboard_arrow_right),
                  ],
                ),
        ),
        actions: [
          buttonContainer(Icons.dashboard, Colors.white, Colors.black),
          buttonContainer(Icons.notifications, Colors.white, Colors.black),
          buttonContainer(
              Icons.satellite_alt_outlined, Colors.white, Colors.black),
          buttonContainer(Icons.bar_chart, Colors.white, Colors.black),
          buttonContainer(Icons.settings, Colors.white, Colors.black),
          buttonContainer(Icons.supervisor_account, Colors.white, Colors.black),
          buttonContainer(Icons.logout, Colors.white, Colors.black),
        ],
      ),
      body: Row(
        children: [
          //Let's start by adding the Navigation Rail
          NavigationRail(
            extended: isExpanded,
            backgroundColor: Colors.black,
            unselectedIconTheme:
                const IconThemeData(color: Colors.white, opacity: 1),
            unselectedLabelTextStyle: const TextStyle(
              color: Colors.white,
            ),
            selectedIconTheme: const IconThemeData(color: Colors.orange),
            selectedLabelTextStyle: const TextStyle(color: Colors.orange),
            selectedIndex: _selectedIndex,
            onDestinationSelected: (int index) {
              setState(() {
                sideBarController.setCurrentPageIndex(index);
                _selectedIndex = index;
              });
            },
            destinations: const [
              // Dashboard
              NavigationRailDestination(
                icon: Icon(Icons.dashboard),
                label: Text("Dashboard"),
              ),
              // Notifications
              NavigationRailDestination(
                icon: Icon(Icons.notifications),
                label: Text("Notifications"),
              ),
              // Satellite Data
              NavigationRailDestination(
                icon: Icon(Icons.satellite_alt_outlined),
                label: Text("Satellite Data"),
              ),
              // Statistics
              NavigationRailDestination(
                icon: Icon(Icons.bar_chart),
                label: Text("Statistics"),
              ),
              // Profile Icon
              NavigationRailDestination(
                icon: Icon(Icons.supervisor_account),
                label: Text("Profile"),
              ),
              // Settings
              NavigationRailDestination(
                icon: Icon(Icons.settings),
                label: Text("Settings"),
              ),

              // Logout
              NavigationRailDestination(
                icon: Icon(Icons.logout),
                label: Text("Logout"),
              ),
            ],
          ),
          // Shows actual page
          Expanded(child: Obx(() => sideBarController.getCurrentPage())),
        ],
      ),
    );
  }

  Container buttonContainer(
      IconData icon, Color backgroundColor, Color iconColor) {
    return Container(
      margin: const EdgeInsets.all(10),
      alignment: Alignment.center,
      width: 37,
      decoration: BoxDecoration(
          color: backgroundColor, borderRadius: BorderRadius.circular(7.5)),
      child: Icon(
        icon,
        color: iconColor,
      ),
    );
  }
}
