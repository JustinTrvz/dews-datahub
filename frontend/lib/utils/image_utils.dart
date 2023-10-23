import 'dart:convert';

import 'package:flutter/material.dart';

class ImageUtils {
  static Widget decodeBase64EncodedImg(base64EncodedImg, widthVal) {
    return Image.memory(base64Decode(base64EncodedImg),
        height: widthVal - 10, fit: BoxFit.fill);
  }
}
