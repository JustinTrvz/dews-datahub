import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';
import 'package:gui/utils/api.dart';
import 'package:gui/utils/firebase_database.dart';
import 'package:gui/utils/firebase_storage.dart';

class AddSidPage extends StatefulWidget {
  const AddSidPage({Key? key, required this.sideBarController})
      : super(key: key);
  final SideBarController sideBarController;

  @override
  State<AddSidPage> createState() => _AddSidPageState();
}

class _AddSidPageState extends State<AddSidPage> {
  final TextEditingController _satelliteTypeController =
      TextEditingController();
  final TextEditingController _areaNameController = TextEditingController();
  final TextEditingController _cityController = TextEditingController();
  final TextEditingController _countryController = TextEditingController();
  final TextEditingController _postalCodeController = TextEditingController();
  final List<DropdownMenuEntry<SatelliteTypeLabel>> satelliteTypeEntries =
      <DropdownMenuEntry<SatelliteTypeLabel>>[];
  final List<SatelliteTypeLabel> _disabledLabels = [
    SatelliteTypeLabel.landsat1,
    SatelliteTypeLabel.landsat2,
    SatelliteTypeLabel.landsat3,
    SatelliteTypeLabel.sentinel2A
  ];
  SatelliteTypeLabel? selectedSatelliteType;
  FilePickerResult? filePickerResult;
  String? fileName;
  PlatformFile? pickedFile;
  bool isUploading = false;
  bool isLoadingFile = false;
  bool saveClicked = false;
  File? fileToDisplay;
  Text fileButtonText = const Text("Select a file...");

  @override
  Widget build(BuildContext context) {
    // Satellite type
    if (satelliteTypeEntries.isEmpty) {
      for (SatelliteTypeLabel satelliteType in SatelliteTypeLabel.values) {
        satelliteTypeEntries.add(
          DropdownMenuEntry<SatelliteTypeLabel>(
            value: satelliteType,
            label: satelliteType.label,
            enabled: !_disabledLabels.contains(satelliteType),
          ),
        );
      }
    }
    _satelliteTypeController.addListener(() {
      setState(() {});
    });
    // Area name
    _areaNameController.addListener(() {
      setState(() {});
    });
    // City
    _cityController.addListener(() {
      setState(() {});
    });
    // Country
    _countryController.addListener(() {
      setState(() {});
    });
    // Postal code
    _postalCodeController.addListener(() {
      setState(() {});
    });

    return Expanded(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: <Widget>[
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                selectFileButton(),
              ],
            ),
            isLoadingFile
                ? const Text(
                    'Upload may take a while... Thanks for being patient!',
                    style: TextStyle(color: Colors.red))
                : const SizedBox(
                    height: 0), // Display warning if a file is selected

            TextFormField(
              controller: _areaNameController,
              decoration: const InputDecoration(labelText: 'Area Name'),
            ),
            TextFormField(
              controller: _cityController,
              decoration: const InputDecoration(labelText: 'City'),
            ),
            TextFormField(
              controller: _countryController,
              decoration: const InputDecoration(labelText: 'Country'),
            ),
            TextFormField(
              controller: _postalCodeController,
              decoration: const InputDecoration(labelText: 'Postal Code'),
            ),
            // Drop-down menu: Satellite type
            selectSatelliteType(),
            // Tail buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Cancel button
                cancelButton(context),
                // Gap between buttons
                const SizedBox(
                  width: 5,
                ),
                // Save button
                saveButton(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void pickFile() async {
    print("pickFile()");
    try {
      setState(() {
        isUploading = false;
        isLoadingFile = true;
        fileButtonText = const Text("Loading file...");
      });

      // Load picked file into memory
      filePickerResult = await FilePicker.platform.pickFiles(
        withData: true,
        type: FileType.custom,
        allowMultiple: false,
        allowedExtensions: ["zip"],
      );

      if (filePickerResult != null) {
        fileName = filePickerResult!.files.first.name;
        pickedFile = filePickerResult!.files.single;
        print("File name: $fileName");
      }

      setState(() {
        isLoadingFile = false;
      }); // Update the screen
    } catch (e) {
      print(e);
    }
  }

  Text getPickedFilename(PlatformFile? pickedFile) {
    if (pickedFile != null) {
      var fileName = pickedFile.name;
      if (fileName.length >= 20) {
        fileName =
            "${fileName.substring(0, 15)}(...).${pickedFile.extension}"; // shortens the displayed file name
      }
      return Text(fileName);
    } else {
      return const Text("Select a file");
    }
  }

  Row selectSatelliteType() {
    selectedSatelliteType = SatelliteTypeLabel.sentinel2B;
    return Row(
      children: [
        const SizedBox(width: 20),
        DropdownMenu<SatelliteTypeLabel>(
          initialSelection: SatelliteTypeLabel.sentinel2B,
          controller: _satelliteTypeController,
          // enableFilter: true,
          // leadingIcon: const Icon(Icons.search),
          label: const Text("Satellite Type"),
          dropdownMenuEntries: satelliteTypeEntries,
          onSelected: (SatelliteTypeLabel? satelliteType) {
            setState(() {
              selectedSatelliteType = satelliteType;
            });
          },
        ),
        const SizedBox(width: 20),
      ],
    );
  }

  ElevatedButton saveButton() {
    return ElevatedButton.icon(
      onPressed: (pickedFile == null)
          ? null
          : () async {
              setState(() {
                saveClicked = true;
              });

              print("Extension: ${pickedFile!.extension}");

              var storagePath = "uploads/sentinel-2b";
              // Upload zip file as extracted directory
              setState(() {
                isUploading = true;
              });
              final String uploadPath = await FirebaseStorageUtils.uploadFile(
                pickedFile!,
                storagePath,
                false,
              );

              // Upload error handling
              if (uploadPath == "") {
                // TODO: show an error message
                print(
                    "File '${pickedFile!.name}' could not be uploaded to storage. uploadPath='$uploadPath'");
              }
              print("Upload done...");

              String satelliteType;
              if (selectedSatelliteType != null) {
                satelliteType = selectedSatelliteType!.label;
              } else {
                satelliteType = "unknown";
              }
              // Send json data to api in backend
              Map<String, dynamic> jsonData = ApiUtils.createUploadJson(
                uploadPath,
                satelliteType,
                "kj23n4kj234n",
                _areaNameController.text,
                _cityController.text,
                int.parse(_postalCodeController.text),
                _countryController.text,
              );

              int apiOk = await ApiUtils.sendUploadNotification(jsonData);

              // Api error handling
              if (apiOk <= 0) {
                print("Could not send json data to api. apiOk=$apiOk");
              }
              print("Send upload notification");

              setState(() {
                isUploading = false;
              });

              setState(() {
                // Add up calculations
                FirebaseDatabaseUtils.getUserById("123")
                    .calculationsInProgress += 1; // TODO: get actual user
                // Jump back to "Satellite Data" page
                widget.sideBarController.index.value = 2;
              });
            },
      icon: (isUploading) ? saveLoadingIcon() : const Icon(Icons.save),
      label: (saveClicked) ? const Text("Uploading...") : const Text("Save"),
    );
  }

  ElevatedButton cancelButton(BuildContext dialogContext) {
    return ElevatedButton.icon(
      icon: const Icon(Icons.cancel),
      label: const Text("Cancel"),
      onPressed: () {
        widget.sideBarController.index.value =
            2; // jumps to "Satellite Image Data" page
      },
    );
  }

  Container uploadInfoBox() {
    return Container(
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
            padding: EdgeInsets.all(10),
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
    );
  }

  Row selectFileButton() {
    return Row(
      children: [
        ElevatedButton.icon(
          onPressed: () {
            pickFile();
          },
          icon: isLoadingFile
              ? Container(
                  width: 15,
                  height: 15,
                  padding: const EdgeInsets.all(2.0),
                  child: const CircularProgressIndicator(
                    color: Colors.white,
                    strokeWidth: 3,
                  ),
                )
              : const Icon(Icons.upload_file),
          label: (pickedFile != null)
              ? getPickedFilename(pickedFile)
              : fileButtonText,
        ),
        const SizedBox(width: 20),
      ],
    );
  }

  String removeExtension(String fileName) {
    final extension = fileName.split('.').last;

    // List of extensions to exclude from removal (e.g., ".SAFE")
    final excludedExtensions = ['.SAFE'];

    if (extension == extension.toLowerCase() &&
        !excludedExtensions.contains(extension)) {
      return fileName.substring(
          0, fileName.length - (extension.length + 1)); // +1 for the dot
    }

    return fileName;
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

enum SatelliteTypeLabel {
  sentinel2A("Sentinel-2A"),
  sentinel2B("Sentinel-2B"),
  landsat1("Landsat-1"),
  landsat2("Landsat-2"),
  landsat3("Landsat-3");

  const SatelliteTypeLabel(this.label);
  final String label;
}
