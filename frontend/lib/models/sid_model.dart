class SatelliteImageDataModel {
  String sidId;
  String sidImg;
  String areaName;
  String country;
  String city;
  int postalCode;
  String thumbnail;
  String ownerName;
  DateTime? creationTime;
  late double ndvi;
  late String ndviImg;
  late DateTime? ndviCalcDateTime;
  late double water;
  late String waterImg;
  late DateTime? waterCalcDateTime;

  SatelliteImageDataModel({
    this.sidId = "",
    this.sidImg = "",
    this.areaName = "",
    this.country = "",
    this.city = "",
    this.postalCode = 0,
    this.thumbnail = "",
    this.ownerName = "",
    this.creationTime,
    this.ndvi = -1,
    this.ndviImg = "",
    this.ndviCalcDateTime,
    this.water = -1,
    this.waterImg = "",
    this.waterCalcDateTime,
  });

  factory SatelliteImageDataModel.fromJson(Map<String, dynamic> json) {
    print(json["basic"]["owner_id"]);
    return SatelliteImageDataModel(
      sidId: json["basic"]["id"] as String,
      sidImg: json["basic"]["img"] as String,
      areaName: json["basic"]["area_name"] as String,
      country: json["basic"]["country"] as String,
      city: json["basic"]["city"] as String,
      postalCode: int.parse(json["basic"]["postal_code"]),
      thumbnail: "",
      ownerName: json["basic"]["owner_id"] as String,
      creationTime:
          DateTime.parse(json["capture_information"]["generation_time"]).toUtc(),
      ndvi: json["indexes"]["ndvi"]["value"],
      ndviImg: json["indexes"]["ndvi"]["img"] as String,
      ndviCalcDateTime: DateTime.parse(json["indexes"]["ndvi"]["calc_time"]).toUtc(),
      water:json["indexes"]["water"]["value"],
      waterImg: json["indexes"]["water"]["img"] as String,
      waterCalcDateTime: DateTime.parse(json["indexes"]["water"]["calc_time"]).toUtc(),
    );
  }
}
