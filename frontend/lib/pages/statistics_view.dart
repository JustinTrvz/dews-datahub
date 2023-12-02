import 'package:flutter/material.dart';
import 'package:gui/pages/side_bar/side_bar_controller.dart';

class StatisticsPage extends StatefulWidget {
  const StatisticsPage({Key? key, required this.sideBarController}) : super(key: key);
  final SideBarController sideBarController;

  @override
  State<StatisticsPage> createState() => _StatisticsPageState();
}

class _StatisticsPageState extends State<StatisticsPage> {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text("Statistics..."),
    );
  }
}