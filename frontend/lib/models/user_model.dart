class DewsUser {
  String id;
  late List<String> userGroups = [];
  String email;
  String firstName;
  String lastName;
  String streetName;
  int streetNumber;
  int postalCode;
  String country;
  String currency;
  String phoneNumber;
  bool activeUser;
  DateTime? createdTimestamp;
  DateTime? lastModifiedTimestamp;
  // other
  int calculationsInProgress;
  int newFilesCount;
  int notificationsCount;

  DewsUser({
    this.id = "",
    List<String>? userGroups,
    this.email = "",
    this.firstName = "",
    this.lastName = "",
    this.streetName = "",
    this.streetNumber = 0,
    this.postalCode = 0,
    this.country = "",
    this.currency = "Euro",
    this.phoneNumber = "",
    this.activeUser = true,
    this.createdTimestamp,
    this.lastModifiedTimestamp,
    this.calculationsInProgress = 0,
    this.newFilesCount = 0,
    this.notificationsCount = 0,
  });
}
