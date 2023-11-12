import 'package:flutter/material.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';
import 'package:gui/utils/widgets/elapsed_time_widget.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({Key? key, required this.sideBarController})
      : super(key: key);
  final SideBarController sideBarController;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: Center(
        child: Expanded(
          child: Padding(
            padding: const EdgeInsets.only(left: 30, right: 30),
            child: SingleChildScrollView(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Welcome message
                  const Text(
                      'Welcome, Peter Müller!', // TODO: get user's first and last name
                      style: TextStyle(fontSize: 25)),
                  // Gap
                  const SizedBox(
                    height: 10,
                  ),
                  // Dashboard
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      const Flexible(
                        child: Card(
                          child: Padding(
                            padding: EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.satellite_alt_outlined,
                                      size: 26.0,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "Satellite Data",
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
                                  "2 Entries",
                                  style: TextStyle(
                                    fontSize: 36,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(
                                  height: 5.0,
                                ),
                                Text(
                                  "+2 New Entries",
                                  style: TextStyle(
                                    color: Colors.grey,
                                    fontSize: 18,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const Flexible(
                        child: Card(
                          child: Padding(
                            padding: EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.calculate,
                                      size: 26.0,
                                      color: Colors.red,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "Calculations",
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
                                  "2 Calculations",
                                  style: TextStyle(
                                    color: Colors.red,
                                    fontSize: 36,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(
                                  height: 5.0,
                                ),
                                Text(
                                  "+2 New Calculations",
                                  style: TextStyle(
                                    color: Colors.grey,
                                    fontSize: 18,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const Flexible(
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
                                      "Profiles",
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
                                  "1 Profiles",
                                  style: TextStyle(
                                    fontSize: 36,
                                    color: Colors.amber,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(
                                  height: 5.0,
                                ),
                                Text(
                                  "+0 New Profiles",
                                  style: TextStyle(
                                    color: Colors.grey,
                                    fontSize: 18,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      Flexible(
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(18.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Row(
                                  children: [
                                    Icon(
                                      Icons.timer,
                                      size: 26.0,
                                      color: Colors.green,
                                    ),
                                    SizedBox(
                                      width: 15.0,
                                    ),
                                    Text(
                                      "System uptime",
                                      style: TextStyle(
                                        fontSize: 26.0,
                                        color: Colors.green,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    )
                                  ],
                                ),
                                const SizedBox(
                                  height: 20.0,
                                ),
                                ElapsedTimeWidget(
                                    startTime: DateTime.now(),
                                    textColor: Colors.green,
                                    fontWeight: FontWeight.bold),
                                const SizedBox(
                                  height: 5.0,
                                ),
                                Text(
                                  "since ${DateTime.now()}",
                                  style: const TextStyle(
                                    color: Colors.grey,
                                    fontSize: 18,
                                  ),
                                ),
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
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        children: [
                          Text(
                            "Log entries",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 28.0,
                            ),
                          ),
                          SizedBox(
                            height: 10.0,
                          ),
                          Text(
                            "+3 log entries",
                            style: TextStyle(
                                color: Colors.grey,
                                fontSize: 18.0,
                                fontWeight: FontWeight.w400),
                          ),
                        ],
                      ),
                      Container(
                        width: 300.0,
                        child: const TextField(
                          decoration: InputDecoration(
                            hintText: "Search for log entry",
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
                          "Last day",
                          style: TextStyle(
                            color: Colors.deepPurple.shade400,
                          ),
                        ),
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            "Today",
                            style: TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 18),
                          )
                        ],
                      ),
                      Row(
                        children: [
                          DropdownButton(
                              hint: const Text("Filter by"),
                              items: [
                                const DropdownMenuItem(
                                  value: "Date",
                                  child: Text("Date"),
                                ),
                                const DropdownMenuItem(
                                  value: "Comments",
                                  child: Text("Comments"),
                                ),
                                const DropdownMenuItem(
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
                              items: [
                                const DropdownMenuItem(
                                  value: "Date",
                                  child: Text("Date"),
                                ),
                                const DropdownMenuItem(
                                  value: "Comments",
                                  child: Text("Comments"),
                                ),
                                const DropdownMenuItem(
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
                            DataColumn(label: Text("Type")),
                            DataColumn(label: Text("Creation Date")),
                            DataColumn(label: Text("Log details")),
                          ],
                          rows: [
                            DataRow(cells: [
                              const DataCell(Text("0")),
                              const DataCell(Text("ERROR")),
                              DataCell(Text("${DateTime.now()}")),
                              const DataCell(Text("Divison error. id='xyz'")),
                            ]),
                            DataRow(cells: [
                              const DataCell(Text("1")),
                              const DataCell(Text("WARNING")),
                              DataCell(Text("${DateTime.now()}")),
                              const DataCell(Text("List is empty. id='xyz'")),
                            ]),
                            DataRow(cells: [
                              const DataCell(Text("2")),
                              const DataCell(Text("INFO")),
                              DataCell(Text("${DateTime.now()}")),
                              const DataCell(Text("Calculation done for id 'xyz'.")),
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
          ),
        ),
      ),
    );
  }
}
