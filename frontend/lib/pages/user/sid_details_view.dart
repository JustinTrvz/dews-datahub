import "package:flutter/material.dart";
import "package:gui/models/sid_model.dart";
import "package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart";
import "package:gui/utils/firebase_storage.dart";
import 'package:gui/utils/widgets/dews_style.dart';

class SidDetailsPage extends StatefulWidget {
  const SidDetailsPage({super.key, required this.sid, required this.sideBarController});
  final SatelliteDataModel sid;
  final SideBarController sideBarController;

  @override
  State<SidDetailsPage> createState() => _SidDetailsPageState();
}

class _SidDetailsPageState extends State<SidDetailsPage> {
  @override
  Widget build(BuildContext context) {
    return indexListView();
  }

  ListView indexListView() {
    return ListView(
      padding: const EdgeInsets.all(8),
      children: <Widget>[
        sidDetails(),
        const SizedBox(height: 10),
        indexExpansionTile(
          "RGB",
          widget.sid.rgbImgStoragePath,
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              attrContainer("RGB calculation time", widget.sid.creationTime),
            ],
          ),
        ),
        indexExpansionTile(
          "NDVI index",
          widget.sid.ndviImgStoragePath,
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              attrContainer("NDVI value", widget.sid.ndvi),
              attrContainer(
                  "NDVI calculation time", widget.sid.ndviCalcDateTime),
            ],
          ),
        ),
        indexExpansionTile(
          "Moisture Index",
          widget.sid.moistureImgStoragePath,
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              attrContainer("NDVI value", widget.sid.ndvi),
              attrContainer(
                  "NDVI calculation time", widget.sid.ndviCalcDateTime),
            ],
          ),
        )
      ],
    );
  }

  Widget sidDetails() {
    return Row(
      children: [
        GestureDetector(
          onTap: () {
            // Go back to "Satellite data" page
            widget.sideBarController.setPage("satellite-data");
          },
          child: DewsStyle.buttonContainer(Icons.arrow_back_ios_new_outlined, Colors.orange, Colors.black),
        ),
        const Icon(Icons.satellite_alt_outlined),
        const SizedBox(width: 10),
        Text(
          widget.sid.areaName,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        )
      ],
    );
  }

  ExpansionTile indexExpansionTile(
      String indexName, String imgStoragePath, Widget indexDetails) {
    return ExpansionTile(
      title: Text(indexName),
      children: <Widget>[
        indexContainer(indexName, imgStoragePath, indexDetails)
      ],
    );
  }

  Container indexContainer(
      String indexName, String imgStoragePath, Widget indexDetails) {
    double size = 400.0;
    return Container(
      padding: const EdgeInsets.only(left: 15),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(15),
      ),
      child: Row(
        children: [
          SizedBox(
            width: size,
            height: size,
            child: Padding(
              padding: const EdgeInsets.all(5.0),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8.0),
                child: Image.network(
                  FirebaseStorageUtils.generateImgUrl(imgStoragePath),
                  fit: BoxFit.cover,
                ),
              ),
            ),
          ),
          indexDetails,
        ],
      ),
    );
  }

  Container attrContainer(String attrName, attrVal, [int? position]) {
    var edgeInsets = const EdgeInsets.only(left: 5, top: 1, bottom: 1);

    if (position != null) {
      if (position == 0) {
        edgeInsets = const EdgeInsets.only(left: 5, top: 5);
      } else if (position == 1) {
        edgeInsets = const EdgeInsets.only(left: 5, bottom: 5);
      }
    }

    return Container(
      decoration: const BoxDecoration(
        shape: BoxShape.rectangle,
      ),
      child: Padding(
        padding: edgeInsets,
        child: RichText(
          text: TextSpan(children: <TextSpan>[
            TextSpan(
              text: "$attrName: ",
              style: const TextStyle(
                  fontWeight: FontWeight.bold, color: Colors.black),
            ),
            TextSpan(
                text: attrVal.toString(),
                style: const TextStyle(color: Colors.black)),
          ]),
          selectionColor: Colors.black,
        ),
      ),
    );
  }
}
