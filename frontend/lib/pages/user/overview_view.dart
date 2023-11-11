import 'package:flutter/material.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({Key? key, required this.sideBarController}) : super(key: key);
  final SideBarController sideBarController;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: Center(
        child: Text(
          'Welcome, Peter Müller!', // TODO: get user's first and last name
          style: const TextStyle(fontSize: 25),
        ),
      ),
    );
  }
}