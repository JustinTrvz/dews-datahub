import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/admin/admin_overview.dart';
import 'package:gui/pages/user/user_overview.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  @override
  void initState() {
    super.initState();
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersive);

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

    Future.delayed(const Duration(seconds: 1), () {
      Navigator.of(context).pushReplacement(MaterialPageRoute(
        builder: (_) => const AdminOverviewPage(),
        // builder: (_) => UserOverviewPage(
        //   user: user,
        // ),
      ));
    });
  }

  @override
  void dispose() {
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.manual,
        overlays: SystemUiOverlay.values);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: Container(
      width: double.infinity,
      height: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color.fromRGBO(225, 225, 225, 1),
              Colors.white,
              Color.fromRGBO(225, 225, 225, 1)
            ]),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.satellite_outlined,
              size: 80, color: Colors.lightBlue),
          const SizedBox(height: 20),
          const Text(
            "Drought-EWS's Datahub",
            style: TextStyle(
              fontSize: 32,
            ),
          ),
          Container(
            width: 30,
            height: 30,
            padding: const EdgeInsets.all(2.0),
            child: const CircularProgressIndicator(
              color: Colors.lightBlue,
              strokeWidth: 2,
            ),
          ),
        ],
      ),
    ));
  }
}
