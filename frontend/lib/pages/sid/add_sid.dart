import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:gui/firebase_options.dart';
import 'package:gui/utils/database.dart';
import 'package:path/path.dart' as path;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_storage/firebase_storage.dart';

class AddSatelliteImageData extends StatefulWidget {
  const AddSatelliteImageData({super.key});

  static Future show(BuildContext context, void Function()? onFinish) async {
    return showDialog(
        context: context,
        builder: (context) => const AddSatelliteImageData()).then((_) {
      if (onFinish != null) {
        onFinish();
      }
    });
  }

  @override
  State<AddSatelliteImageData> createState() => _AddSatelliteImageDataState();
}

class _AddSatelliteImageDataState extends State<AddSatelliteImageData> {
  final TextEditingController _tfCtrlAreaName = TextEditingController();
  final TextEditingController _tfCtrlCity = TextEditingController();
  final TextEditingController _tfCtrlCountry = TextEditingController();
  final TextEditingController _tfCtrlPostalCode = TextEditingController();
  FilePickerResult? filePickerResult;
  String? fileName;
  PlatformFile? pickedFile;
  bool isUploading = false;
  bool saveClicked = false;
  File? fileToDisplay;

  @override
  Widget build(BuildContext context) {
    // Area name
    _tfCtrlAreaName.addListener(() {
      setState(() {});
    });
    // City
    _tfCtrlCity.addListener(() {
      setState(() {});
    });
    // Country
    _tfCtrlCountry.addListener(() {
      setState(() {});
    });
    // Postal code
    _tfCtrlPostalCode.addListener(() {
      setState(() {});
    });

    return showAddDialog(context);
  }

  void pickFile() async {
    print("pickFile()");
    try {
      setState(() {
        isUploading = false;
      });

      filePickerResult = await FilePicker.platform.pickFiles(
        withReadStream: true,
        type: FileType.any,
        allowMultiple: false,
      );

      if (filePickerResult != null) {
        fileName = filePickerResult!.files.first.name;
        pickedFile = filePickerResult!.files.single;
        fileToDisplay = File(pickedFile!.path.toString());
        print("File name: $fileName");
      }

      setState(() {}); // Update the screen
    } catch (e) {
      print(e);
    }
  }

  Text getPickedFilename(PlatformFile? pickedFile) {
    if (pickedFile != null) {
      var filePath = pickedFile.path.toString();
      var fileExtension = path.extension(filePath);
      var fileNameWithoutExtension = path.basenameWithoutExtension(filePath);
      var fileName = path.basename(filePath);
      if (fileNameWithoutExtension.length >= 20) {
        fileName =
            "${fileNameWithoutExtension.substring(0, 15)}(...)$fileExtension"; // shortens the displayed file name
      }
      return Text(fileName);
    } else {
      return const Text("Select a file");
    }
  }

  AlertDialog showAddDialog(BuildContext dialogContext) {
    return AlertDialog(
      title: const Text("Add a new entry"),
      content: SingleChildScrollView(
        child: Column(
          children: [
            // File upload
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: () {
                    pickFile();
                  },
                  icon: const Icon(Icons.upload_file),
                  label: (pickedFile != null)
                      ? getPickedFilename(pickedFile)
                      : const Text("Select a file..."),
                ),
              ],
            ),

            // Text fields
            attrRow("Areaname", _tfCtrlAreaName),
            attrRow("City", _tfCtrlCity),
            attrRow("Country", _tfCtrlCountry),
            attrRow("Postal code", _tfCtrlPostalCode),

            // Upload info
            Container(
              margin: const EdgeInsets.only(top: 15),
              decoration: BoxDecoration(
                color: Colors.red[300],
                borderRadius: BorderRadius.circular(10),
                border: Border.all(),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.5),
                    spreadRadius: 2.5,
                    blurRadius: 3.5,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: const Row(
                children: [
                  Icon(Icons.priority_high),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(
                      "Uploading a file may take a while...\nPlease be patient! Thank you!",
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      // Buttons
      actions: <Widget>[
        ElevatedButton.icon(
          icon: const Icon(Icons.cancel),
          label: const Text("Cancel"),
          onPressed: () {
            Navigator.pop(dialogContext);
          },
        ),
        ElevatedButton.icon(
          onPressed: (pickedFile == null)
              ? null
              : () async {
                  setState(() {
                    saveClicked = true;
                  });

                  print("Extension: ${pickedFile!.extension}");

                  final int? uploadResponseCode =
                      await Database.uploadFile(pickedFile!);
                  setState(() {
                    isUploading = true;
                  });

                  final int creationResponseCode =
                      await Database.createSidEntry(
                    fileName!,
                    _tfCtrlAreaName.text,
                    _tfCtrlCity.text,
                    _tfCtrlCountry.text,
                    int.parse(_tfCtrlPostalCode.text),
                  );

                  if (uploadResponseCode != 201 ||
                      creationResponseCode != 201) {
                    // TODO: show an error message
                    print(
                        "Error: creationResponseCode='$creationResponseCode', uploadResponseCode='$uploadResponseCode'");
                  }

                  setState(() {
                    isUploading = false;
                  });

                  Navigator.pop(context); // TODO: rewrite! do not use this!
                },
          icon: (isUploading) ? saveLoadingIcon() : const Icon(Icons.save),
          label: const Text("Save"),
        ),
      ],
    );
  }

  Container saveLoadingIcon() {
    return Container(
      width: 24,
      height: 24,
      padding: const EdgeInsets.all(2.0),
      child: const CircularProgressIndicator(
        color: Colors.white,
        strokeWidth: 3,
      ),
    );
  }

  SnackBar uploadSnackbar() {
    return SnackBar(
      content: const Text(
          'Uploading a file may take a while... Please be patient! Thank you!'),
      duration: const Duration(seconds: 15),
      action: SnackBarAction(
        label: 'Cancel Upload',
        onPressed: () {
          // TODO: implement cancel upload
        },
      ),
    );
  }

  Row attrRow(String attrName, TextEditingController textEditingController) {
    return Row(
      children: [
        Text("${attrName}: "),
        Expanded(
          child: TextField(
              controller: textEditingController,
              decoration: InputDecoration(hintText: "$attrName")),
        )
      ],
    );
  }
}
