import 'dart:async';
import 'package:flutter/material.dart';

class ElapsedTimeWidget extends StatefulWidget {
  final DateTime startTime;
  final Color textColor;
  final FontWeight fontWeight;

  ElapsedTimeWidget({required this.startTime, required this.textColor, required this.fontWeight});

  @override
  _ElapsedTimeWidgetState createState() => _ElapsedTimeWidgetState();
}

class _ElapsedTimeWidgetState extends State<ElapsedTimeWidget> {
  late DateTime startTime;
  late Duration elapsedTime;
  late Timer timer;

  @override
  void initState() {
    super.initState();
    startTime = widget.startTime;
    elapsedTime = const Duration();
    timer = Timer.periodic(const Duration(seconds: 1), _updateElapsedTime);
  }

  void _updateElapsedTime(Timer timer) {
    setState(() {
      elapsedTime = DateTime.now().difference(startTime);
    });
  }

  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    String formattedTime =
        '${elapsedTime.inHours}:${(elapsedTime.inMinutes % 60).toString().padLeft(2, '0')}:${(elapsedTime.inSeconds % 60).toString().padLeft(2, '0')}';

    return Text(
      formattedTime,
      style: TextStyle(
        fontSize: 36,
        color: widget.textColor,
        fontWeight: widget.fontWeight,
      ),
    );
  }
}
