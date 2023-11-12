import "package:flutter/material.dart";
import "package:gui/models/sid_model.dart";
import "package:gui/utils/firebase_storage.dart";

class SidDetailsPage extends StatefulWidget {
  const SidDetailsPage({super.key, required this.sid});
  final SatelliteDataModel sid;

  @override
  State<SidDetailsPage> createState() => _SidDetailsPageState();
}

class _SidDetailsPageState extends State<SidDetailsPage> {
  @override
  Widget build(BuildContext context) {
    return Container(
      // width: 200.0,
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: [
          const Row(
            children: [Text("RGB Image")],
          ),
          Row(
            children: [
              SizedBox(
                        width: 400,
                        height: 300.0,
                        child: Padding(
                          padding: const EdgeInsets.all(5.0),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8.0),
                            child: Image.network(
                              FirebaseStorageUtils.generateImgUrl(
                                  widget.sid.rgbImgStoragePath),
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                      ),
            ],
          )
        ],
      ),
    );
  }
}
