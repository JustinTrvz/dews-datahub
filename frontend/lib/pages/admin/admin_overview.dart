import 'package:flutter/material.dart';
import 'package:gui/models/notification_model.dart';
import 'package:gui/models/sid_model.dart';
import 'package:gui/pages/sid/add_sid.dart';
import 'package:gui/pages/sid/show_sid.dart';
import 'package:gui/utils/database.dart';
import 'package:gui/utils/image_utils.dart';

class AdminOverviewPage extends StatefulWidget {
  const AdminOverviewPage({super.key});

  @override
  State<AdminOverviewPage> createState() => _AdminOverviewPageState();
}

class _AdminOverviewPageState extends State<AdminOverviewPage> {
  List<SatelliteImageDataModel> sidList = [];
  List<NotificationModel> notificationList = [];
  int _activeIndex = 1; // Overview page
  List<Widget> _pages = [];

  void _changeActivePage(int index) {
    setState(() {
      _activeIndex = index;
    });
  }

  @override
  void initState() {
    _pages = [
      profilesWidget(),
      overviewWidget(),
      notificationsWidget(),
    ];
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    _pages = <Column>[
      profilesWidget(),
      overviewWidget(),
      notificationsWidget(),
    ];

    return FutureBuilder<int>(
      future: _getSidEntries(),
      builder: ((context, snapshot) {
        return getHomeScaffold(context);
      }),
    );
  }

  Scaffold getHomeScaffold(BuildContext context) {
    return Scaffold(
      appBar: appBar(),
      backgroundColor: Colors.white,
      body: _pages[_activeIndex],
      floatingActionButton: SizedBox(
          height: 75,
          width: 200,
          child: FloatingActionButton.extended(
            onPressed: () {
              AddSatelliteImageData.show(context, () {});
            },
            icon: const Icon(Icons.add),
            label: const Text("Add new entry"),
          )),
      bottomNavigationBar: BottomNavigationBar(
        items: <BottomNavigationBarItem>[
          bottomNavBarItem(Icons.person, "Profiles"),
          bottomNavBarItem(Icons.view_list, "Overview"),
          bottomNavBarItem(Icons.notifications, "Notifications"),
        ],
        currentIndex: _activeIndex,
        selectedItemColor: Colors.amber[800],
        onTap: _changeActivePage,
      ),
    );
  }

  Column profilesWidget() {
    return const Column(
      children: [
        Center(
          child: Text("pro"),
        )
      ],
    );
  }

  Column notificationsWidget() {
    return Column(
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 20),
          child: Text(
            'Satellite Image Areas',
            style: TextStyle(
              color: Colors.black,
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        const SizedBox(
          height: 10,
        ),
        Container(
          height: 700,
          color: Colors.amber,
          child: createNotifications(),
        ),
      ],
    );
  }

  ListView createNotifications() {
    notificationList.add(NotificationModel(
      notificationId: "lfjrertpojert",
      userId: "rgemrglkermg",
      category: "Upload",
      message: "Upload of file 'xyz' is done.",
      thumbnail: "",
    ));
    return ListView.separated(
      itemCount: notificationList.length,
      scrollDirection: Axis.vertical,
      padding: const EdgeInsets.only(top: 10, left: 5, right: 5, bottom: 10),
      separatorBuilder: (context, index) => const SizedBox(
        height: 5,
      ),
      itemBuilder: (context, index) {
        double widthVal = 400.0;
        return GestureDetector(
          onTap: () {},
          child: Container(
            width: widthVal,
            decoration: BoxDecoration(
              color: Colors.lightBlue,
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
                          child: ImageUtils.decodeBase64EncodedImg(
                              notificationList[index].thumbnail, widthVal),
                        ),
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    attrContainer("Category", notificationList[index].category),
                    attrContainer("Message", notificationList[index].message),
                    attrContainer(
                        "DateTime", notificationList[index].creationTime),
                  ],
                )
              ],
            ),
          ),
        );
      },
    );
  }

  Column overviewWidget() {
    return Column(
      children: [
        _searchField(),
        const SizedBox(
          height: 15,
        ),
        Column(
          children: [
            const Padding(
              padding: EdgeInsets.only(left: 20),
              child: Text(
                'Satellite Image Areas',
                style: TextStyle(
                  color: Colors.black,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(
              height: 10,
            ),
            Container(
              height: 700,
              color: Colors.amber,
              child: createSidEntries(),
            ),
          ],
        ),
      ],
    );
  }

  BottomNavigationBarItem bottomNavBarItem(IconData iconData, String label) {
    return BottomNavigationBarItem(
      icon: Icon(iconData),
      label: label,
    );
  }

  Future<int> _getSidEntries() async {
    print("-> -> -> -> -> -> -> -> ->");
    sidList = await Database.getSidBatch();
    print("SIDLIST_LENGTH: ${sidList.length}");
    print(DateTime.now());
    print("<- <- <- <- <- <- <- <- <-");
    return sidList.length;
  }

  Widget createSidEntries() {
    var listView = ListView.separated(
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
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          ShowSatelliteImageData(sidId: sidList[index].sidId)));
            },
            child: Container(
              width: widthVal,
              decoration: BoxDecoration(
                color: Colors.green,
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
                            child: ImageUtils.decodeBase64EncodedImg(
                                sidList[index].sidImg, widthVal),
                          ),
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // General information
                      attrContainer("ID", sidList[index].sidId, 0),
                      attrContainer("Name", sidList[index].areaName),
                      attrContainer("Location",
                          "${sidList[index].postalCode} ${sidList[index].city}, ${sidList[index].country}"),
                      attrContainer("Owner", sidList[index].ownerName),
                      attrContainer(
                          "Creation time", sidList[index].creationTime, 1),
                      // Indexes
                      attrContainer("NDVI", sidList[index].ndvi, 0),
                      attrContainer("NDVI (last calculation)",
                          sidList[index].ndviCalcDateTime),
                      attrContainer("Water index", sidList[index].water),
                      attrContainer("Water index (last calculation)",
                          sidList[index].waterCalcDateTime, 1),
                    ],
                  ),
                ],
              ),
            ),
          );
        }));

        if (sidList.isEmpty) {
           return const Center(child: CircularProgressIndicator());
        } else {
          return listView;
        }
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

  Container _searchField() {
    return Container(
      margin: const EdgeInsets.only(top: 10, left: 25, right: 25),
      decoration: BoxDecoration(boxShadow: [
        BoxShadow(
            color: Colors.black.withOpacity(0.15),
            blurRadius: 40,
            spreadRadius: 0.0)
      ]),
      child: TextField(
        decoration: InputDecoration(
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.all(15),
          hintText: "Search for satellite image data",
          hintStyle: const TextStyle(
            color: Colors.grey,
            fontSize: 15,
          ),
          prefixIcon: const Icon(Icons.search),
          suffixIcon: const SizedBox(
            width: 20,
            child: IntrinsicHeight(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  VerticalDivider(
                    color: Colors.black,
                    indent: 5,
                    endIndent: 5,
                    thickness: 0.1,
                  ),
                  Icon(Icons.filter_alt),
                ],
              ),
            ),
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }

  AppBar appBar() {
    return AppBar(
      title: const Text(
        "Remote Sensing Analysis",
        style: TextStyle(
          color: Colors.black,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
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
            getLoadingDialog();
            setState(() {});
            Navigator.of(context).pop();
          },
          child: buttonContainer(Icons.refresh),
        ),
        GestureDetector(
          onTap: () {},
          child: buttonContainer(Icons.notifications),
        ),
        GestureDetector(
          onTap: () {},
          child: buttonContainer(Icons.question_mark),
        )
      ],
    );
  }

  Container buttonContainer(IconData icon) {
    return Container(
      margin: const EdgeInsets.all(10),
      alignment: Alignment.center,
      width: 37,
      decoration: BoxDecoration(
          color: Colors.black, borderRadius: BorderRadius.circular(10)),
      child: Icon(icon),
    );
  }

  Future<dynamic> getLoadingDialog() {
    return showDialog(
        context: context,
        builder: (_) {
          return const Dialog(
            backgroundColor: Colors.white,
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(
                    height: 15,
                  ),
                  Text("Loading..."),
                ],
              ),
            ),
          );
        });
  }
}
