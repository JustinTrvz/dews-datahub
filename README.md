# Drought Early Warning System's Datahub (DE-DH)

# Start guide
1. [Install Firebase Emulator Suite.](#firebase)
2. [Install Python.](#python)
3. [Install Flutter.](#flutter)
4. [Download satellite images.](#satellite-images)
5. [Start the software.](#start-software)

# Firebase
## Firebase Emulator Suite Installation (Development)
For further information or in case of issues look at [this official documentation](https://firebase.google.com/docs/emulator-suite/connect_and_prototype).
1. Install Firebase CLI or update to its latest version
   - **Install:** `curl -sL firebase.tools | bash`
   - **Update:** `curl -sL firebase.tools | upgrade=true bash`
2. Initialize your Firebase project.
   - `firebase init`
   - Choose the existing project `drought-ews-dev` or create a new one called `drought-ews-dev`.
   - Choose "Authentication", "Realtime Database" and "Storage".
3. Start the emulators.
   - `cd drought-ews`
   - `make emulators`
4. Open the UI URL for the database and storage.
   - After the start of the emulators the URLs for the API and the UI of the database and the storage are shown.
   - Open one of the emulator UI URLs in a browser.
   - You will see a user interface. The emulators are working. Great!

## Firebase (Production)
- _TBD..._

# Python
## Install Python
- **Linux:** `sudo apt update && apt install -y python3`
- **MacOS:** [Python Downloads MacOS](https://www.python.org/downloads/macos/) _or_ `sudo brew install python3`
- **Windows:** [Python Downloads Windows](https://www.python.org/downloads/windows/)

## Virtual Environment
- Setup an environment and install the required packages:
  - `cd drought-ews`
  - `make setup`

## Edit Python path
1. Add this project's path to the system environment variable `$PYTHONPATH`.
   - `export PYTHONPATH=$PYTHONPATH:<root to this project>`
     - e.g. `export PYTHONPATH="$PYTHONPATH:/home/user/Peter/Git/drought-ews"`
2. Check if the changes were applied by executing `echo $PYTHONPATH`.
3. If this worked then add the command from step one to the `~/.bashrc` file.
   - Use Vim, Gedit or any other editor to open `~/.bashrc` with privileges
     - e.g. `sudo gedit ~/.bashrc`
     - Add these the following lines to the file: 
       ```
       # Python path for 'Moisture Detector' project
       export PYTHONPATH="$PYTHONPATH:<root to this project>"
       ```

# Flutter
## Install Flutter
### Using Snap (Linux):
1. Install Flutter.
   - `sudo snap install flutter --classic`
2. Check if installation is correct.
   - `flutter doctor`

### Using Git (all OS):
1. Create a new directory for the Flutter SDK.
   - `mkdir ~/flutter`
   - `git clone https://github.com/flutter/flutter.git`
   - `export PATH="$PATH:/home/dev/flutter/bin"`
     - Add this environment variable to the `~/.bashrc` file if you want.

# Satellite Images
- **Source:** [Copernicus Open Access Hub](https://scihub.copernicus.eu/dhus/#/home)
- **Mission:** `Sentinel-2`
- **Satellite Platform:** `S2B_*`

### How to download satellite images manually
For a video tutorial see this [YouTube video](https://www.youtube.com/watch?v=sMax7wkUrlI).
1. Open [Copernicus Open Access Hub](https://scihub.copernicus.eu/dhus/#/home).
2. Login with your account or register first.
3. Select the selection tool on the right side.
4. Select your desired area on the map.
5. Click on the top left on the burger menu to open the advanced search.
6. Fill out the "Sensing Period" (_e.g. 2023/07/01 - 2023/07/10_).
7. Leave "Ingestion Period" empty!
8. Select "Mission: Sentinel-2".
9. Select "Satellite Platform" with value "S2B_*".
10. Fill out "Cloud Cover" with the value "[0 TO 9.4]".
11. Click on the magnifier button.
12. Download any product that you want by clicking the download button.

# Start software
1. You will need *three* terminals.
2. First terminal starts the Firebase Emulator suite: `make emulators`
3. Second terminal start the Python backend: `make main`
4. Third terminal start the Flutter web app: `make flutter`
5. Do it in this order and a browser window will open automatically after approximately 30 seconds.

## Upload satellite image data
1. Click on _Add new entry_.
2. Select the downloaded zip archive.
3. While the data is loading fill out the form.
4. Click on _Save_ when the data has finished loading.
5. Please be patient while the data is uploading.
6. After some time the calculation from the backend are done and are displayed as entries.
7. If no entries are displayed, click the refresh icon in the top right corner.

# More information
## Config file
Configs are saved in the config Python file (`config.py`).