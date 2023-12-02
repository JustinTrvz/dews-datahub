from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase

from backend.models.satellite_data.utils.sid_logger import SidLogger
from backend.database.firebase import *
from backend.models.satellite_data.utils.file_utils import FileUtils
from backend.config import *
from backend.api.uploads_api import uploads_api
from backend.api.basics_api import basics_api

# Logger
logger = SidLogger()

# SQLAlchemy init
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
auth = HTTPBasicAuth()

# Flask init
app = Flask(FLASK_NAME, root_path=ROOT_PATH)
# CORS Config
CORS(app)
# Flask SQLAlchemy database config
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Flask API blueprints
app.register_blueprint(uploads_api)
app.register_blueprint(basics_api)
# Rest of config
app.app_context().push()
db.init_app(app)

import backend.database.models
import backend.db_cli

if __name__ == "__main__":
    # Files + directories
    FileUtils.create_file_directories()
    print("Created file directories...")

    # Start Flask
    app.run(host=FLASK_HOST, port=FLASK_PORT,
            debug=DEBUG_STATUS, threaded=True)
    print("Started Flask...")
