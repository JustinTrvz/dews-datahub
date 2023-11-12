import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SideBarController extends GetxController {
  RxInt pageIndex = 0.obs;
  List<Widget> pagesList = []; // Contains all pages
  Map<String, int> pagesMap = {}; // Maps identifier to index position in 'pagesList'

  /// Add a page widget by passing its `id` (e.g. `home`) and the widget itself as `page`.
  bool addPage(String id, Widget page) {
    // Check if id exists in `pagesMap`
    if (pagesMap.containsKey(id)) {
      return false;
    }

    // Add to list
    pagesList.add(page);
    // Get index position of widget in `pagesList`
    int idxPos;
    if (pagesList.isEmpty) {
      idxPos = 0;
    } else {
      idxPos = pagesList.length - 1;
    }
    // Add to map
    pagesMap[id] = idxPos;
    return true;
  }

  /// Returns widget's index position in `pagesList`.
  /// 
  /// Id is the identifier of the widget which should be previously specified using `addPage(String id, Widget page)`.
  int _getIndexPosition(String id) {
    return pagesMap[id] as int;
  }

  Widget getCurrentPage() {
    return pagesList[pageIndex.value];
  }

  Widget getPageById(String id) {
    return getPageByIndex(_getIndexPosition(id));
  }

  Widget getPageByIndex(int index) {
    return pagesList[index];
  }

  void setCurrentPageIndex(int index) {
    pageIndex.value = index;
  }

  void setPage(String id) {
    setCurrentPageIndex(_getIndexPosition(id));
  }

  bool pageExists(String id) {
    return pagesMap.containsKey(id);
  }

}
