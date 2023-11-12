import 'package:flutter/material.dart';

class DewsStyle {

  static Container buttonContainer(
      IconData icon, Color backgroundColor, Color iconColor) {
    return Container(
      margin: const EdgeInsets.all(10),
      alignment: Alignment.center,
      height: 37,
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