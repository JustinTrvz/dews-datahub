import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:gui/pages/admin/admin_overview.dart';

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

    Future.delayed(const Duration(seconds: 2), () {
      Navigator.of(context).pushReplacement(MaterialPageRoute(
        builder: (_) => const AdminOverviewPage(),
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
          Icon(Icons.satellite_outlined, size: 80, color: Colors.pink),
          SizedBox(height: 20),
          const Text(
            "Drought-EWS Datahub",
            style: TextStyle(
              fontSize: 32,
            ),
          ),
          Container(
            width: 30,
            height: 30,
            padding: const EdgeInsets.all(2.0),
            child: const CircularProgressIndicator(
              color: Colors.pink,
              strokeWidth: 2,
            ),
          ),
        ],
      ),
    ));
  }
}
