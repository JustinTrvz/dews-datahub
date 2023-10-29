from flask import Blueprint, jsonify

basics_api = Blueprint("basics_api", __name__)


@basics_api.route("/")
def home():
    response = {
        "info": "This is the 'Drought EWS' API."
    }
    return jsonify(response), 200