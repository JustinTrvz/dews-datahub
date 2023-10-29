import 'package:flutter/material.dart';
import 'package:gui/models/sid_model.dart';
import 'package:gui/utils/database.dart';
import 'package:gui/utils/firebase_storage.dart';

class ShowSatelliteImageData extends StatefulWidget {
  final SatelliteImageDataModel sid;

  const ShowSatelliteImageData({super.key, required this.sid});

  @override
  State<ShowSatelliteImageData> createState() => _ShowSatelliteImageDataState();
}

class _ShowSatelliteImageDataState extends State<ShowSatelliteImageData> {
  SatelliteImageDataModel sidModel = SatelliteImageDataModel();

  // void _loadSidModel() {
  //   Database.getSidById(widget.sidId)
  //       .then((value) => setState(() => sidModel = value));
  // }

  @override
  void initState() {
    print("IIIDDD: ${sidModel.id}");
    sidModel = widget.sid;
    super.initState();
    // WidgetsBinding.instance.addPostFrameCallback((_) => _loadSidModel());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: appBar(),
      body: SingleChildScrollView(
        child: Column(children: [
          imageSizedBox(400.0, sidModel.rgbImgStoragePath),
          Text("ID: ${sidModel.id}"),
          Text("Area name: ${sidModel.areaName}"),
          Text(
              "Location: ${sidModel.postalCode} ${sidModel.city}, ${sidModel.country}"),
          Text("Owner: ${sidModel.userId}"),
          Text("Creation time: ${sidModel.creationTime}"),
          imageSizedBox(400.0, sidModel.ndviImgStoragePath),
          Text("NDVI: ${sidModel.ndvi}"),
          Text("NDVI (last calculation): ${sidModel.ndviCalcDateTime}"),
          imageSizedBox(400.0, sidModel.moistureImgStoragePath),
          Text("Water index: ${sidModel.moisture}"),
          Text("Water index (last calculation): ${sidModel.moistureCalcDateTime}"),
        ]),
      ),
    );
  }

  SizedBox imageSizedBox(double widthVal, String storagePath) {
    print(FirebaseStorageUtils.generateImgUrl(storagePath));
    return SizedBox(
      width: widthVal,
      child: Padding(
        padding: const EdgeInsets.all(5.0),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8.0),
          child: Image.network(FirebaseStorageUtils.generateImgUrl(storagePath)),
        ),
      ),
    );
  }

  AppBar appBar() {
    return AppBar(
      title: Row(
        children: [
          GestureDetector(
            onTap: () {
                Navigator.pushNamed(context, '/');
            },
            child: Container(
              margin: const EdgeInsets.all(10),
              alignment: Alignment.center,
              width: 37,
              height: 37,
              decoration: BoxDecoration(
                  color: Colors.black, borderRadius: BorderRadius.circular(10)),
              child: const Icon(Icons.arrow_back),
            ),
          ),
          Text(
            sidModel.areaName == "" ? "None" : sidModel.areaName,
            style: const TextStyle(
              color: Colors.black,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
      backgroundColor: Colors.transparent,
      elevation: 0.0,
      centerTitle: true,
      leading: GestureDetector(
        child: Container(
          margin: const EdgeInsets.all(10),
          alignment: Alignment.center,
          decoration: BoxDecoration(
              color: Colors.black, borderRadius: BorderRadius.circular(10)),
          child: const Icon(Icons.menu),
        ),
      ),
      actions: [
        GestureDetector(
          onTap: () {
            setState(() {});
          },
          child: Container(
            margin: const EdgeInsets.all(10),
            alignment: Alignment.center,
            width: 37,
            decoration: BoxDecoration(
                color: Colors.black, borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.refresh),
          ),
        ),
        GestureDetector(
          onTap: () {},
          child: Container(
            margin: const EdgeInsets.all(10),
            alignment: Alignment.center,
            width: 37,
            decoration: BoxDecoration(
                color: Colors.black, borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.question_mark),
          ),
        )
      ],
    );
  }
}
