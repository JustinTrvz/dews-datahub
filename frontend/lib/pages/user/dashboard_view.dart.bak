import 'package:flutter/material.dart';
import 'package:gui/models/user_model.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key, required this.user}) : super(key: key);
  final DewsUser user;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  //setting the expansion function for the navigation rail
  bool isExpanded = false;
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return sideNavBar();
  }

  Scaffold sideNavBar() {
    return Scaffold(
    appBar: AppBar(
      title: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Icon
          Icon(Icons.satellite),
          // Gap
          SizedBox(
            width: 5,
          ),
          Text(
            "DEWS's DataHub",
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
            ),
          ),
        ],
      ),
      backgroundColor: Colors.black,
      leading: GestureDetector(
        onTap: () {
          setState(() {
            isExpanded = !isExpanded;
          });
        },
        child: const Icon(Icons.menu),
      ),
    ),
    body: Row(
      children: [
        //Let's start by adding the Navigation Rail
        NavigationRail(
          extended: isExpanded,
          backgroundColor: Colors.black,
          unselectedIconTheme:
              const IconThemeData(color: Colors.white, opacity: 1),
          unselectedLabelTextStyle: const TextStyle(
            color: Colors.white,
          ),
          selectedIconTheme: const IconThemeData(color: Colors.lightBlue),
          selectedIndex: _selectedIndex,
          onDestinationSelected: (int index) {
            setState(() {
              _selectedIndex = index;
            });
          },
          destinations: [
            // Profile Icon
            NavigationRailDestination(
              icon: const Icon(Icons.supervisor_account),
              label: Text("${widget.user.firstName} ${widget.user.lastName}"),
            ),
            // Satellite Data
            const NavigationRailDestination(
              icon: Icon(Icons.satellite_alt_outlined),
              label: Text("Satellite Data"),
            ),
            // Statistics
            const NavigationRailDestination(
              icon: Icon(Icons.bar_chart),
              label: Text("Statistics"),
            ),
            // Settings
            const NavigationRailDestination(
              icon: Icon(Icons.settings),
              label: Text("Settings"),
            ),
            // Logout
            const NavigationRailDestination(
              icon: Icon(Icons.logout),
              label: Text("Logout"),
            ),
          ],
        ),
        Expanded(
          child: _getPage(_selectedIndex),
        ),
      ],
    ),
    //let's add the floating action button
    floatingActionButton: FloatingActionButton(
      onPressed: () {},
      child: const Icon(Icons.add),
      backgroundColor: Colors.deepPurple.shade400,
    ),
  );
  }

  Widget _getPage(int index) {
    switch (index) {
      case 0:
        return dashboardPage();
      case 1:
        return Center(
          child: const Text("111"),
        );
      default:
      return dashboardPage();
    }
  }

  Padding dashboardPage() {
    return Padding(
            padding: const EdgeInsets.all(60.0),
            child: SingleChildScrollView(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  //let's add the navigation menu for this project
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        onPressed: () {
                          //let's trigger the navigation expansion
                          setState(() {
                            isExpanded = !isExpanded;
                          });
                        },
                        icon: const Icon(Icons.menu),
                      ),
                      const CircleAvatar(
                        backgroundImage: NetworkImage(
                            "https://www.pngall.com/wp-content/uploads/5/Profile-Avatar-PNG.png"),
                        radius: 26.0,
                      ),
                    ],
                  ),
                  const SizedBox(
                    height: 20.0,
                  ),
                  //Now let's start with the dashboard main rapports
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      Flexible(
                        child: Card(
                          child: Padding(
                            padding: EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.article,
                                      size: 26.0,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "Articles",
                                      style: TextStyle(
                                        fontSize: 26.0,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    )
                                  ],
                                ),
                                SizedBox(
                                  height: 20.0,
                                ),
                                Text(
                                  "6 Articles",
                                  style: TextStyle(
                                    fontSize: 36,
                                    fontWeight: FontWeight.bold,
                                  ),
                                )
                              ],
                            ),
                          ),
                        ),
                      ),
                      Flexible(
                        child: Card(
                          child: Padding(
                            padding: EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.comment,
                                      size: 26.0,
                                      color: Colors.red,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "Comments",
                                      style: TextStyle(
                                        color: Colors.red,
                                        fontSize: 26.0,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    )
                                  ],
                                ),
                                SizedBox(
                                  height: 20.0,
                                ),
                                Text(
                                  "+32 Comments",
                                  style: TextStyle(
                                    color: Colors.red,
                                    fontSize: 36,
                                    fontWeight: FontWeight.bold,
                                  ),
                                )
                              ],
                            ),
                          ),
                        ),
                      ),
                      Flexible(
                        child: Card(
                          child: Padding(
                            padding: EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.people,
                                      size: 26.0,
                                      color: Colors.amber,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "Subscribers",
                                      style: TextStyle(
                                        fontSize: 26.0,
                                        color: Colors.amber,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    )
                                  ],
                                ),
                                SizedBox(
                                  height: 20.0,
                                ),
                                Text(
                                  "3.2M Subscribers",
                                  style: TextStyle(
                                    fontSize: 36,
                                    color: Colors.amber,
                                    fontWeight: FontWeight.bold,
                                  ),
                                )
                              ],
                            ),
                          ),
                        ),
                      ),
                      Flexible(
                        child: Card(
                          child: Padding(
                            padding: EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.monetization_on_outlined,
                                      size: 26.0,
                                      color: Colors.green,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "Revenue",
                                      style: TextStyle(
                                        fontSize: 26.0,
                                        color: Colors.green,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    )
                                  ],
                                ),
                                SizedBox(
                                  height: 20.0,
                                ),
                                Text(
                                  "2.300 \$",
                                  style: TextStyle(
                                    fontSize: 36,
                                    color: Colors.green,
                                    fontWeight: FontWeight.bold,
                                  ),
                                )
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  //Now let's set the article section
                  const SizedBox(
                    height: 30.0,
                  ),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        children: [
                          Text(
                            "6 Articles",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 28.0,
                            ),
                          ),
                          SizedBox(
                            height: 10.0,
                          ),
                          Text(
                            "3 new Articles",
                            style: TextStyle(
                                color: Colors.grey,
                                fontSize: 18.0,
                                fontWeight: FontWeight.w400),
                          ),
                        ],
                      ),
                      SizedBox(
                        width: 300.0,
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: "Type Article Title",
                            prefixIcon: Icon(Icons.search),
                            border: OutlineInputBorder(
                              borderSide: BorderSide(
                                color: Colors.black26,
                              ),
                            ),
                          ),
                        ),
                      )
                    ],
                  ),
                  const SizedBox(
                    height: 40.0,
                  ),

                  //let's set the filter section
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TextButton.icon(
                        onPressed: () {},
                        icon: Icon(
                          Icons.arrow_back,
                          color: Colors.deepPurple.shade400,
                        ),
                        label: Text(
                          "2022, July 14, July 15, July 16",
                          style: TextStyle(
                            color: Colors.deepPurple.shade400,
                          ),
                        ),
                      ),
                      Row(
                        children: [
                          DropdownButton(
                              hint: const Text("Filter by"),
                              items: const [
                                DropdownMenuItem(
                                  value: "Date",
                                  child: Text("Date"),
                                ),
                                DropdownMenuItem(
                                  value: "Comments",
                                  child: Text("Comments"),
                                ),
                                DropdownMenuItem(
                                  value: "Views",
                                  child: Text("Views"),
                                ),
                              ],
                              onChanged: (value) {}),
                          const SizedBox(
                            width: 20.0,
                          ),
                          DropdownButton(
                              hint: const Text("Order by"),
                              items: const [
                                DropdownMenuItem(
                                  value: "Date",
                                  child: Text("Date"),
                                ),
                                DropdownMenuItem(
                                  value: "Comments",
                                  child: Text("Comments"),
                                ),
                                DropdownMenuItem(
                                  value: "Views",
                                  child: Text("Views"),
                                ),
                              ],
                              onChanged: (value) {}),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(
                    height: 40.0,
                  ),
                  //Now let's add the Table
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      DataTable(
                          headingRowColor: MaterialStateProperty.resolveWith(
                              (states) => Colors.grey.shade200),
                          columns: const [
                            DataColumn(label: Text("ID")),
                            DataColumn(label: Text("Article Title")),
                            DataColumn(label: Text("Creation Date")),
                            DataColumn(label: Text("Views")),
                            DataColumn(label: Text("Comments")),
                          ],
                          rows: [
                            DataRow(cells: [
                              const DataCell(Text("0")),
                              const DataCell(
                                  Text("How to build a Flutter Web App")),
                              DataCell(Text("${DateTime.now()}")),
                              const DataCell(Text("2.3K Views")),
                              const DataCell(Text("102Comments")),
                            ]),
                            DataRow(cells: [
                              const DataCell(Text("1")),
                              const DataCell(
                                  Text("How to build a Flutter Mobile App")),
                              DataCell(Text("${DateTime.now()}")),
                              const DataCell(Text("21.3K Views")),
                              const DataCell(Text("1020Comments")),
                            ]),
                            DataRow(cells: [
                              const DataCell(Text("2")),
                              const DataCell(
                                  Text("Flutter for your first project")),
                              DataCell(Text("${DateTime.now()}")),
                              const DataCell(Text("2.3M Views")),
                              const DataCell(Text("10K Comments")),
                            ]),
                          ]),
                      //Now let's set the pagination
                      const SizedBox(
                        height: 40.0,
                      ),
                      Row(
                        children: [
                          TextButton(
                            onPressed: () {},
                            child: const Text(
                              "1",
                              style: TextStyle(color: Colors.deepPurple),
                            ),
                          ),
                          TextButton(
                            onPressed: () {},
                            child: const Text(
                              "2",
                              style: TextStyle(color: Colors.deepPurple),
                            ),
                          ),
                          TextButton(
                            onPressed: () {},
                            child: const Text(
                              "3",
                              style: TextStyle(color: Colors.deepPurple),
                            ),
                          ),
                          TextButton(
                            onPressed: () {},
                            child: const Text(
                              "See All",
                              style: TextStyle(color: Colors.deepPurple),
                            ),
                          ),
                        ],
                      )
                    ],
                  )
                ],
              ),
            ),
          );
  }
}
