import 'package:flutter/material.dart';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:gui/firebase_options.dart';
import 'package:gui/pages/splash_screen.dart';

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
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      initialRoute: "/",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(fontFamily: 'Poppins'),
      home: const SplashScreen(),
      // home: const AdminOverviewPage(),
    );
  }
}
