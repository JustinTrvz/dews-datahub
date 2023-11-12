import 'package:flutter/material.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/side_navigation_bar/side_nav_bar_controller.dart';
import 'package:gui/utils/firebase_database.dart';

class ProfilePage extends StatefulWidget {
const ProfilePage({Key? key, required this.sideBarController}) : super(key: key);
  final SideBarController sideBarController;
  
  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  late TextEditingController emailController;
  late TextEditingController firstNameController;
  late TextEditingController lastNameController;
  late TextEditingController streetNameController;
  late TextEditingController streetNumberController;
  late TextEditingController postalCodeController;
  late TextEditingController countryController;
  late TextEditingController currencyController;
  late TextEditingController phoneNumberController;

  late DewsUser originalUser; // Store the original user data.

  @override
  void initState() {
    super.initState();

    originalUser = FirebaseDatabaseUtils.getUserById("123"); // Store the original user data.

    // Initialize the text controllers with the user's data.
    emailController = TextEditingController(text: originalUser.email);
    firstNameController = TextEditingController(text: originalUser.firstName);
    lastNameController = TextEditingController(text: originalUser.lastName);
    streetNameController = TextEditingController(text: originalUser.streetName);
    streetNumberController =
        TextEditingController(text: originalUser.streetNumber.toString());
    postalCodeController =
        TextEditingController(text: originalUser.postalCode.toString());
    countryController = TextEditingController(text: originalUser.country);
    currencyController = TextEditingController(text: originalUser.currency);
    phoneNumberController =
        TextEditingController(text: originalUser.phoneNumber);
  }

  void discardChanges() {
    setState(() {
      // Reset the text controllers to their original values
      emailController.text = originalUser.email;
      firstNameController.text = originalUser.firstName;
      lastNameController.text = originalUser.lastName;
      streetNameController.text = originalUser.streetName;
      streetNumberController.text = originalUser.streetNumber.toString();
      postalCodeController.text = originalUser.postalCode.toString();
      countryController.text = originalUser.country;
      currencyController.text = originalUser.currency;
      phoneNumberController.text = originalUser.phoneNumber;
    });
  }

  @override
  void dispose() {
    // Dispose of text controllers when the widget is disposed.
    emailController.dispose();
    firstNameController.dispose();
    lastNameController.dispose();
    streetNameController.dispose();
    streetNumberController.dispose();
    postalCodeController.dispose();
    countryController.dispose();
    currencyController.dispose();
    phoneNumberController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: <Widget>[
            const Row(
              children: [
                Icon(Icons.supervisor_account),
                Text(
                  'Profile',
                  style: TextStyle(fontSize: 25),
                ),
              ],
            ),
            const SizedBox(height: 20),
            // Non-editable attributes
            ListTile(
              title: const Text('User ID'),
              subtitle: Text(originalUser.id),
            ),
            ListTile(
              title: const Text('User Groups'),
              subtitle: Text(originalUser.userGroups.join(', ')),
            ),
            ListTile(
              title: const Text('Active User'),
              subtitle: Text(originalUser.activeUser.toString()),
            ),
            ListTile(
              title: const Text('Created Timestamp'),
              subtitle: Text(originalUser.createdTimestamp?.toString() ?? 'N/A'),
            ),
            ListTile(
              title: const Text('Last Modified Timestamp'),
              subtitle:
                  Text(originalUser.lastModifiedTimestamp?.toString() ?? 'N/A'),
            ),

            // Editable attributes
            Row(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Expanded(
                  child: Column(
                    children: <Widget>[
                      TextFormField(
                        controller: emailController,
                        decoration: const InputDecoration(labelText: 'Email'),
                      ),
                      TextFormField(
                        controller: firstNameController,
                        decoration: const InputDecoration(labelText: 'First Name'),
                      ),
                      TextFormField(
                        controller: lastNameController,
                        decoration: const InputDecoration(labelText: 'Last Name'),
                      ),
                      TextFormField(
                        controller: streetNameController,
                        decoration: const InputDecoration(labelText: 'Street Name'),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    children: <Widget>[
                      TextFormField(
                        controller: streetNumberController,
                        decoration: const InputDecoration(labelText: 'Street Number'),
                      ),
                      TextFormField(
                        controller: postalCodeController,
                        decoration: const InputDecoration(labelText: 'Postal Code'),
                      ),
                      TextFormField(
                        controller: countryController,
                        decoration: const InputDecoration(labelText: 'Country'),
                      ),
                      TextFormField(
                        controller: currencyController,
                        decoration: const InputDecoration(labelText: 'Currency'),
                      ),
                      TextFormField(
                        controller: phoneNumberController,
                        decoration: const InputDecoration(labelText: 'Phone Number'),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Discard changed
                ElevatedButton(
                  onPressed: () {
                    discardChanges();
                  },
                  child: const Text('Discard'),
                ),
                // Gap between buttons
                const SizedBox(
                  width: 5,
                ),
                // Save changes
                ElevatedButton(
                  onPressed: () {
                    // TODO: Implement the logic to save changes here.
                  },
                  child: const Text('Save'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
