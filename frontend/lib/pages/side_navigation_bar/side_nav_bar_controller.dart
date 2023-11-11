import 'package:get/get.dart';
import 'package:gui/models/user_model.dart';
import 'package:gui/pages/sid/add_sid.dart';
import 'package:gui/pages/user/logout_view.dart';
import 'package:gui/pages/user/notifications_view.dart';
import 'package:gui/pages/user/overview_view.dart';
import 'package:gui/pages/user/profile_view.dart';
import 'package:gui/pages/user/settings_view.dart';
import 'package:gui/pages/user/sid_view.dart';
import 'package:gui/pages/user/statistics_view.dart';

class SideBarController extends GetxController {
  RxInt index = 0.obs;
  var pages = [];
}
