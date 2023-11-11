import "package:flutter/material.dart";
import "package:gui/models/user_model.dart";
import "package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart";
import "package:gui/utils/firebase_database.dart";
import "package:gui/utils/firebase_storage.dart";

class NotificationsPage extends StatefulWidget {
const NotificationsPage({Key? key, required this.sideBarController}) : super(key: key);
  final SideBarController sideBarController;
  
  @override
  State<NotificationsPage> createState() => _NotificationsPageState();
}

class _NotificationsPageState extends State<NotificationsPage> {
  List<dynamic> notificationsList = [];

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: FutureBuilder(
        future: getNotificationEntries(),
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
                            color: Colors.lightBlue,
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
                    return notificationsEntriesListView(snapshot);
                  }
                }
              }

              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Row 1
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.check_box, color: Colors.orange),
                      SizedBox(
                        width: 5,
                      ),
                      Text(
                        "No new notifications available.",
                        style: TextStyle(
                          fontSize: 25,
                        ),
                      ),
                    ],
                  ),
                  // Gap between rows
                  const SizedBox(
                    height: 5,
                  ),
                  // Row 2
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      FloatingActionButton.extended(
                        onPressed: () {
                          setState(() {
                            // refreshes page
                          });
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text("Refresh page"),
                        backgroundColor: Colors.orange,
                      )
                    ],
                  ),
                ],
              );
          }
        },
      ),
    );
  }

  Future<List<dynamic>> getNotificationEntries() async {
    print("-> -> -> -> -> -> -> -> ->");
    List<dynamic> response = await FirebaseDatabaseUtils.getNotificationEntries("123"); // returns [<error code>, <sid list>]

    // Check if is empty
    if (response.isEmpty) {
      print("Empty notifications entries list");
      return response;
    }
    print("Response: $response");

    print("<- <- <- <- <- <- <- <- <-");
    return response;
  }

  Widget notificationsEntriesListView(AsyncSnapshot snapshot) {
    notificationsList = snapshot.data!; // previously checked if has data

    return ListView.separated(
        itemCount: notificationsList.length,
        scrollDirection: Axis.vertical,
        padding: const EdgeInsets.only(top: 10, left: 5, right: 5, bottom: 10),
        separatorBuilder: (context, index) => const SizedBox(
              height: 5,
            ),
        itemBuilder: ((context, index) {
          double widthVal = 400.0;
          return GestureDetector(
            onTap: () {
              // TODO: show notification details
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
                        child: Padding(
                          padding: const EdgeInsets.all(5.0),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8.0),
                            child: Image.network(
                              FirebaseStorageUtils.generateImgUrl(
                                  notificationsList[index]
                                      .thumbnailStoragePath),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // General information
                      attrContainer("ID", notificationsList[index].id, 0),
                      attrContainer("User", notificationsList[index].userId),
                      attrContainer(
                          "Category", notificationsList[index].category),
                      attrContainer("Creation time",
                          notificationsList[index].creationTime),
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
        color: Colors.white,
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
