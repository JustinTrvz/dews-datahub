class FileUtils {
  static String removeExtension(String fileName) {
    final RegExp lowerCaseExtensionRegex = RegExp(r'(\.[a-z]+)$');
    final match = lowerCaseExtensionRegex.firstMatch(fileName);

    if (match != null) {
      return fileName.replaceRange(match.start, match.end, '');
    }

    return fileName;
  }

  static getFirstPathComponent(String path) {
    List<String> splittedPath = path.split("/");
    return splittedPath[0];
  }
}
