import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:archive/archive.dart';
import 'package:gui/utils/file_utils.dart';
import 'package:path_provider/path_provider.dart';

class FirebaseStorageUtils {
  static const HtmlEscape htmlEscape = HtmlEscape();

  /// Uploads [file] to the desired Firebase [storagePath].
  ///
  /// If an archive is passed as [file] the archive will be extracted locally.
  /// In case of an already existing directory in the storage at `'[storagePath]/<archiveName>'`the upload process will be aborted.
  /// Otherwise the extracted files will be recursively uploaded to the storage.
  ///
  /// The Firebase storage path where the file/directory is saved will be returned. Same for already existing files/directories.
  static Future<String> uploadFile(
      PlatformFile file, String storagePath, bool overwrite) async {
    // TODO: implement overwrite option!
    try {
      // Check file's extension
      final String extension = file.extension!.toLowerCase();
      if (extension == 'zip') {
        print("File '${file.name}' is an archive file.");

        // Extract archive's content
        final List<int> bytes = file.bytes!;
        final Archive archive = ZipDecoder().decodeBytes(bytes);
        print("Decoded bytes from '${file.name}'...");

        // Generate upload path and check if directory exists
        String dirName = ""; // overwritten in 'Get directory name'
        String uploadPath = ""; // overwritten in 'Get directory name'

        for (final file in archive) {
          final fileName = file.name;

          // Generate directory name
          if (uploadPath == "") {
            dirName = FileUtils.getFirstPathComponent(fileName);
            uploadPath = "$storagePath/$dirName";
          }

          // Get directory's file list
          final Reference dirRef = FirebaseStorage.instance.ref(uploadPath);
          final ListResult dirResult = await dirRef.list();

          // Check if directory is empty
          if (dirResult.items.isNotEmpty) {
            print(
                "Directory '$uploadPath' already exists in Firebase Storage. Stopping upload process...");
            return uploadPath;
          } else {
            print(
                "Directory '$uploadPath' does not exist. Upload will be continued...");
            break; // only the first file is needed
          }
        }

        // Upload archive's content
        for (final file in archive) {
          final fileName = file.name;

          // Check if is file
          if (file.isFile) {
            final List<int> data = file.content as List<int>;
            // Upload the extracted file to the specified storage path
            await FirebaseStorage.instance
                .ref("$storagePath/$fileName")
                .putData(Uint8List.fromList(data),
                    SettableMetadata(contentType: 'application/octet-stream'));
          }
        }

        print("Extracted archive upload done! uploadPath='$uploadPath'");
        return uploadPath;
      } else {
        // other file types
        await FirebaseStorage.instance.ref(storagePath).putData(file.bytes!,
            SettableMetadata(contentType: 'application/octet-stream'));
        print(
            "Unknown file type upload done! uploadPath='$storagePath/${file.name}'");
        return "$storagePath/${file.name}";
      }
    } catch (e) {
      print("File upload error. file.name='${file.name}', error='$e'");
      return "";
    }
  }

  static Future<bool> fileExists(String storagePath) async {
    Reference storageRef = FirebaseStorage.instance.ref().child(storagePath);
    try {
      await storageRef.getDownloadURL();
      print("File '$storagePath' exists.");
      return true;
    } catch (e) {
      print("File '$storagePath' does not exist: '$e'");
      return false;
    }
  }

  static Future<File?> downloadFile(String storagePath) async {
    try {
      Directory appDocDir = await getApplicationDocumentsDirectory();
      File localFile = File('${appDocDir.path}/downloaded_file');
      await FirebaseStorage.instance.ref(storagePath).writeToFile(localFile);
      return localFile;
    } catch (e) {
      print("File download error: '$e'");
      return null;
    }
  }

  static String generateImgUrl(String storagePath) {
    String projectName = "drought-ews-dev.appspot.com";
    storagePath = Uri.encodeComponent(storagePath);
    String apiEndpoint = "http://127.0.0.1:9199/v0/b/${projectName}/o";
    String suffix = "?alt=media";

    // sid%2Fsentinel-2b%2F8bed5746-7f33-4eb2-af42-ae68b319463f%2Fimages%2Frgb%2F8bed5746-7f33-4eb2-af42-ae68b319463f_rgb_20231029_145817.png
    return "$apiEndpoint/$storagePath$suffix";
  }
}
