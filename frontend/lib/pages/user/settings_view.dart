import 'package:flutter/material.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({Key? key, required this.sideBarController})
      : super(key: key);
  final SideBarController sideBarController;

  @override
  _SettingsPageState createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  // Define fictitious settings and their initial values
  bool setting1 = false;
  bool setting2 = true;
  bool setting3 = false;
  bool setting4 = true;
  bool setting5 = false;
  bool setting6 = true;
  bool setting7 = false;
  bool setting8 = true;
  bool setting9 = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.settings),
                Text(
                  'Settings',
                  style: TextStyle(fontSize: 25),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ListTile(
                        title: Text('Setting 1'),
                        trailing: Switch(
                          value: setting1,
                          onChanged: (value) {
                            setState(() {
                              setting1 = value;
                            });
                          },
                        ),
                      ),
                      ListTile(
                        title: Text('Setting 2'),
                        trailing: Switch(
                          value: setting2,
                          onChanged: (value) {
                            setState(() {
                              setting2 = value;
                            });
                          },
                        ),
                      ),
                      ListTile(
                        title: Text('Setting 3'),
                        trailing: Switch(
                          value: setting3,
                          onChanged: (value) {
                            setState(() {
                              setting3 = value;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ListTile(
                        title: Text('Setting 4'),
                        trailing: Switch(
                          value: setting4,
                          onChanged: (value) {
                            setState(() {
                              setting4 = value;
                            });
                          },
                        ),
                      ),
                      ListTile(
                        title: Text('Setting 5'),
                        trailing: Switch(
                          value: setting5,
                          onChanged: (value) {
                            setState(() {
                              setting5 = value;
                            });
                          },
                        ),
                      ),
                      ListTile(
                        title: Text('Setting 6'),
                        trailing: Switch(
                          value: setting6,
                          onChanged: (value) {
                            setState(() {
                              setting6 = value;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ListTile(
                        title: Text('Setting 7'),
                        trailing: Switch(
                          value: setting7,
                          onChanged: (value) {
                            setState(() {
                              setting7 = value;
                            });
                          },
                        ),
                      ),
                      ListTile(
                        title: Text('Setting 8'),
                        trailing: Switch(
                          value: setting8,
                          onChanged: (value) {
                            setState(() {
                              setting8 = value;
                            });
                          },
                        ),
                      ),
                      ListTile(
                        title: Text('Setting 9'),
                        trailing: Switch(
                          value: setting9,
                          onChanged: (value) {
                            setState(() {
                              setting9 = value;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ), // here
            SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Discard changes
                ElevatedButton(
                  onPressed: () {
                    // discardChanges(); // Call the function to reset changes.
                  },
                  child: Text('Discard'),
                ),
                // Gap between buttons
                const SizedBox(
                  width: 5,
                ),
                // Save changes
                ElevatedButton(
                  onPressed: () {
                    // saveChanges(); // Call the function to save changes.
                  },
                  child: Text('Save'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
