import "package:flutter/material.dart";
import "package:gui/models/user_model.dart";
import 'package:gui/pages/side_bar/side_bar_controller.dart';
import 'package:gui/pages/sid/sid_details_view.dart';
import "package:gui/utils/firebase_database.dart";
import "package:gui/utils/firebase_storage.dart";

class SatelliteDataPage extends StatefulWidget {
  const SatelliteDataPage({Key? key, required this.sideBarController})
      : super(key: key);
  final SideBarController sideBarController;

  @override
  State<SatelliteDataPage> createState() => _SatelliteDataPageState();
}

class _SatelliteDataPageState extends State<SatelliteDataPage> {
  List<dynamic> sidList = [];
  DewsUser user = FirebaseDatabaseUtils.getUserById("123");

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          widget.sideBarController.setPage("satellite-data/add");
        },
        icon: const Icon(Icons.add),
        label: const Text("Add new entry"),
        backgroundColor: Colors.orange,
      ),
      body: Container(
        color: Colors.white,
        child: FutureBuilder(
            future: getSidEntries(),
            initialData: const [],
            builder: (BuildContext context, AsyncSnapshot snapshot) {
              switch (snapshot.connectionState) {
                case ConnectionState.none:
                  return const Text("Restart needed (top right corner)!");
                case ConnectionState.waiting:
                  return const SizedBox(
                    width: double.infinity,
                    child: Center(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            height: 20,
                            width: 20,
                            child: Center(
                              child: CircularProgressIndicator(
                                color: Colors.orange,
                                strokeWidth: 2,
                              ),
                            ),
                          ),
                          SizedBox(
                            width: 7.5,
                          ),
                          Text(
                            "Loading...",
                            style: TextStyle(
                              fontSize: 25,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                default:
                  if (snapshot.hasError) {
                    return Text("Error: '${snapshot.error}'");
                  } else {
                    if (snapshot.data != null) {
                      if (snapshot.data.isNotEmpty) {
                        return sidEntriesListView(snapshot);
                      }
                    }
                  }

                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // Row 1
                          const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.file_copy,
                                color: Colors.orange,
                              ),
                              SizedBox(width: 5),
                              Text(
                                "No satellite image data available.",
                                style: TextStyle(
                                  fontSize: 25,
                                ),
                              ),
                            ],
                          ),
                          // Gap between rows
                          const SizedBox(height: 5),
                          // Row 2
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              // Refresh page button
                              FloatingActionButton.extended(
                                onPressed: () {
                                  setState(() {
                                    // refreshes current page
                                  });
                                },
                                icon: const Icon(Icons.refresh),
                                label: const Text("Refresh page"),
                                backgroundColor: Colors.orange,
                              ),
                              // Gap between buttons
                              const SizedBox(
                                width: 7.5,
                              ),
                            ],
                          ),
                          // Gap
                          const SizedBox(
                            height: 5,
                          ),

                          // Calculations in progrss
                          Visibility(
                            visible: user.calculationsInProgress >= 1,
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                // Loading icon
                                Container(
                                  width: 15,
                                  height: 15,
                                  padding: const EdgeInsets.all(2.0),
                                  child: const CircularProgressIndicator(
                                    color: Colors.orange,
                                    strokeWidth: 1,
                                  ),
                                ),
                                // Gap between icon and text
                                SizedBox(width: 2.5),
                                // Text
                                Text(
                                  "Currently ${user.calculationsInProgress} calculation(s) in progress...", // TODO: get calculationsInProgress count from user object
                                  style: const TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey,
                                  ),
                                )
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  );
              }
            }),
      ),
    );
  }

  Future<List<dynamic>> getSidEntries() async {
    List<dynamic> response = await FirebaseDatabaseUtils
        .getSidEntries(); // returns [<error code>, <sid list>]

    // Check if is empty
    if (response.isEmpty) {
      print("Empty sid entries list");
      return response;
    }
    print("Response: $response");

    return response;
  }

  Widget sidEntriesListView(AsyncSnapshot snapshot) {
    sidList = snapshot.data!; // previously checked if has data
    return ListView.separated(
        itemCount: sidList.length,
        scrollDirection: Axis.vertical,
        padding: const EdgeInsets.only(top: 10, left: 5, right: 5, bottom: 10),
        separatorBuilder: (context, index) => const SizedBox(
              height: 5,
            ),
        itemBuilder: ((context, index) {
          double widthVal = 400.0;
          return GestureDetector(
            onTap: () {
              // Check if sid details page exists
              if (!widget.sideBarController
                  .pageExists("satellite-data/${sidList[index].id}")) {
                // Create and add sid details page
                Widget sidDetailsPage = SidDetailsPage(
                  sid: sidList[index],
                  sideBarController: widget.sideBarController,
                );
                bool ok = widget.sideBarController.addPage(
                    "satellite-data/${sidList[index].id}", sidDetailsPage);
                if (!ok) {
                  print(
                      "Could not show SID details page. id='${sidList[index].id}'");
                }
              }
              // Go to sid details page
              widget.sideBarController
                  .setPage("satellite-data/${sidList[index].id}");
            },
            child: Container(
              width: widthVal,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(15),
              ),
              child: Row(
                children: [
                  Column(
                    children: [
                      SizedBox(
                        width: widthVal,
                        height: 300.0,
                        child: Padding(
                          padding: const EdgeInsets.all(5.0),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8.0),
                            child: Image.network(
                              FirebaseStorageUtils.generateImgUrl(
                                  sidList[index].rgbImgStoragePath),
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header
                      Row(
                        children: [
                          Icon(Icons.satellite_alt_outlined, size: 20),
                          SizedBox(width: 5),
                          RichText(
                            text: TextSpan(
                              text: "${sidList[index].satelliteType}",
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      // General information
                      attrContainer("ID", sidList[index].id, 0),
                      attrContainer("Name", sidList[index].areaName),
                      attrContainer("Location",
                          "${sidList[index].postalCode} ${sidList[index].city}, ${sidList[index].country}"),
                      attrContainer("User ID", sidList[index].userId, 1),
                      // Time data
                      attrContainer("Entry creation time",
                          sidList[index].creationTime, 0),
                      attrContainer("Product start time",
                          sidList[index].productStartTime),
                      attrContainer(
                          "Product stop time", sidList[index].productStopTime),
                      attrContainer("Data generation time",
                          sidList[index].generationTime, 1),

                      // Indexes
                      attrContainer("NDVI", sidList[index].ndvi, 0),
                      attrContainer("NDVI (last calculation)",
                          sidList[index].ndviCalcDateTime),
                      attrContainer("Moisture index", sidList[index].moisture),
                      attrContainer("Moisture index (last calculation)",
                          sidList[index].moistureCalcDateTime, 1),
                    ],
                  ),
                ],
              ),
            ),
          );
        }));
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
