class SatelliteDataModel {
  // basic
  String id;
  String areaName;
  String country;
  String city;
  int postalCode;
  String userId;
  DateTime? creationTime;
  String satelliteType;
  // images/rgb
  String rgbImgStoragePath;
  // images/indexes/ndvi
  late double ndvi;
  late String ndviImgStoragePath;
  late DateTime? ndviCalcDateTime;
  // images/indexes/water
  late double moisture;
  late String moistureImgStoragePath;
  late DateTime? moistureCalcDateTime;
  // bound latitudes
  double? northBoundLatitude;
  double? eastBoundLatitude;
  double? southBoundLatitude;
  double? westBoundLatitude;
  // capture information
  late DateTime? productStartTime;
  late DateTime? productStopTime;
  String processingLevel;
  String productType;
  late DateTime? generationTime;

  SatelliteDataModel({
    // basic
    this.id = "", //
    this.userId = "",
    this.areaName = "",
    this.country = "",
    this.city = "",
    this.postalCode = 0,
    this.creationTime,
    this.satelliteType = "", // default value
    // images/rgb
    this.rgbImgStoragePath = "",
    // images/indexes/ndvi
    this.ndvi = -1.0,
    this.ndviImgStoragePath = "",
    this.ndviCalcDateTime,
    // images/indexes/moisture
    this.moisture = -1,
    this.moistureImgStoragePath = "",
    this.moistureCalcDateTime,
    // bound latitudes
    this.northBoundLatitude,
    this.eastBoundLatitude,
    this.southBoundLatitude,
    this.westBoundLatitude,
    // capture information
    this.productStartTime,
    this.productStopTime,
    this.processingLevel = "",
    this.productType = "",
    this.generationTime,
  });

  factory SatelliteDataModel.fromJson(Map<String, dynamic> json) {
    print(json["basic"]["user_id"]);
    Map<String, dynamic> basicJson = json["basic"];
    Map<String, dynamic> captureInfoJson = json["capture_information"];
    Map<String, dynamic> boundLatitudesJson = json["bound_latitudes"];
    Map<String, dynamic> imagesJson = json["images"];
    Map<String, dynamic> indexesJson = imagesJson["indexes"];
    // print("- - - - - - - - - - -");
    // print(basicJson);
    // print("- - - - - - - - - - -");
    // print(captureInfoJson);
    // print("- - - - - - - - - - -");
    // print(boundLatitudesJson);
    // print("- - - - - - - - - - -");
    // print(imagesJson);
    // print("- - - - - - - - - - -");
    // print(basicJson["postal_code"].runtimeType);
    // print("- - - - - - - - - - -");
    return SatelliteDataModel(
      // basics
      areaName: basicJson["area_name"] as String,
      city: basicJson["city"] as String,
      country: basicJson["country"] as String,
      creationTime: DateTime.parse(basicJson["creation_time"]).toUtc(),
      id: basicJson["id"] as String,
      postalCode: basicJson["postal_code"],
      satelliteType: basicJson["satellite_type"],
      userId: basicJson["user_id"] as String,

      // bound latitudes
      // northBoundLatitude: double.parse(boundLatitudesJson["north"]),
      // eastBoundLatitude: double.parse(boundLatitudesJson["east"]),
      // southBoundLatitude: double.parse(boundLatitudesJson["south"]),
      // westBoundLatitude: double.parse(boundLatitudesJson["west"]),
      eastBoundLatitude: boundLatitudesJson["east"],
      northBoundLatitude: boundLatitudesJson["north"],
      southBoundLatitude: boundLatitudesJson["south"],
      westBoundLatitude: boundLatitudesJson["west"],

      // file paths (not needed)

      // capture info
      generationTime:
          DateTime.parse(captureInfoJson["generation_time"]).toUtc(),
      processingLevel: captureInfoJson["processing_level"],
      productStartTime:
          DateTime.parse(captureInfoJson["product_start_time"]).toUtc(),
      productStopTime:
          DateTime.parse(captureInfoJson["product_stop_time"]).toUtc(),
      productType: captureInfoJson["product_type"],

      // images/rgb
      rgbImgStoragePath: imagesJson["rgb"]["img_path_storage"],

      // images/indexes/ndvi
      ndviCalcDateTime:
          DateTime.parse(indexesJson["ndvi"]["calc_time"]).toUtc(),
      ndviImgStoragePath: indexesJson["ndvi"]["img_path_storage"],
      ndvi: indexesJson["ndvi"]["value"],

      // images/indexes/moisture
      moistureCalcDateTime:
          DateTime.parse(indexesJson["moisture"]["calc_time"]).toUtc(),
      moistureImgStoragePath:
          indexesJson["moisture"]["img_path_storage"],
      moisture: indexesJson["moisture"]["value"],
    );
  }
}
