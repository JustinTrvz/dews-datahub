# Satellite image datahub

# Firebase
## Firebase Emulator Suite (Local Development/Testing)
For further information or in case of issues look at [this official documentation](https://firebase.google.com/docs/emulator-suite/connect_and_prototype).
1. Install Firebase CLI or update to its latest version
   - `curl -sL firebase.tools | bash`
2. Initialize your Firebase project.
   - `firebase init`
   - Choose an existing project or create a new one.
   - Choose "Realtime Database" and "Storage".
3. Start the emulators.
   - `firebase emulators:start`
4. Open the UI URL for the database and storage.
   - After the start of the emulators the URLs for the API and the UI of the database and the storage are shown.
   - Open one of the emulator UI URLs in a browser.
   - You will see a user interface. The emulators are working. Great!


## Virtual Environment
- Create a new virtual environment: `python -m venv ./venv`
- Activate the new virtual environement: `source venv/bin/activate`
- Install all required packages: `pip install -r requirements.txt`

## Edit Python path
1. Add this project's path to the system environment variable `$PYTHONPATH`.
   - `export PYTHONPATH=$PYTHONPATH:<root to this project>`
     - e.g. `export PYTHONPATH="$PYTHONPATH:/home/user/Git/moisture_detector"`
2. Check if the changes were applied by executing `echo $PYTHONPATH`.
3. If this worked then add the command from step one to the `~/.bashrc` file.
   - Use Vim, Gedit or any other editor to open `~/.bashrc` with privileges
     - e.g. `sudo gedit ~/.bashrc`
     - Add these the following lines to the file: 
       ```
       # Python path for 'Moisture Detector' project
       export PYTHONPATH="$PYTHONPATH:<root to this project>"
       ```

## Satellite Images
- **Source:** [Copernicus Scihub/Open Access Hub](https://scihub.copernicus.eu/dhus/#/home)
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

## Config file
Configs are saved in the config YAML file (_e.g. `config.yml`_).

### Example config file
This is a config file that is used in development.
```
environment:
  debug: True
logger:
  log_file_location: "app.log"
  log_format: "[%(asctime)s] | %(levelname)s - %(module)s.%(funcName)s[%(lineno)d]: %(message)s"
  log_date_format: "%Y-%m-%d %H:%M:%S"
database:
  type: "MySQL"
  host: "localhost"
  user: "admin"
  password: "cGFzc3dvcmQ="
  database_name: "remote_sensing_analysis"
```