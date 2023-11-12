import "package:flutter/material.dart";

class ErrorPage extends StatelessWidget {
  const ErrorPage({super.key, required this.route});
  final String route;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Error Page"),
      ),
      body: Center(
        child: Text("Page '$route' does not exist!"),
      ),
    );
  }
}