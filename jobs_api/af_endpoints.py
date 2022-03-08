import json
import pathlib
import uuid as uuidlib

import celery_util
from flask import jsonify, render_template, request
from flask.blueprints import Blueprint


af_apis = Blueprint("af", __name__, url_prefix="/v1")


@af_apis.route("/t/<name>", methods=["GET"])
def get_name(name):
    # todo read from AFDB
    return name


# TODO: this will be replaced by the AFDB connector instead of being held in memory
global analysis_type
analysis_type = [
    {"name": "DSSAT Simulation", "id": str(uuidlib.uuid4())}
]

@af_apis.route("/analysis-type", methods=["GET"])
def get_analysis_type():
    # todo read from AFDB
    return jsonify({"status": "ok", "response": analysis_type}), 200


@af_apis.route("/analysis-type", methods=["POST"])
def post_analysis_type():
    content = request.json
    if "name" not in content:
        return jsonify({"status": "error", "message": "missing 'name'"}), 400
    if not content["name"]:
        return jsonify({"status": "error", "message": "'name' is empty"}), 400

    id = str(uuidlib.uuid4())
    # TODO add to AFDB instead
    analysis_type.append({"name": content["name"], "id": id})

    print(json.dumps(analysis_type))

    return jsonify({"status": "ok", "id": id}), 201


@af_apis.route("/datasources", methods=["GET"])
def get_data_source():
    path = pathlib.Path(__file__).parent.absolute()
    with open(str(path) + "/datasourceconfig.json") as f:
        data = json.load(f)

    return data


@af_apis.route("/test", methods=["GET"])
def test():
    return render_template("loginExample.html")


@af_apis.route("/test/redirect", methods=["GET"])
def testredirect():
    return render_template("loginExample.html")


@af_apis.route("/test/dssat", methods=["POST"])
def testdssat():
    content = request.json
    # req = Request(uuid=str(uuidlib.uuid4()))
    # db.session.add(req)
    # db.session.commit()
    celery_util.send_task(process_name="run_dssat", args=(content,), queue="DSSAT", routing_key="DSSAT")
    return jsonify({"status": "ok", "id": 1})

@af_apis.route("/test/dssat", methods=["GET"])
def get_simulation_summary():

    celery_util.send_task(process_name="get_summary", args=(), queue="DSSAT", routing_key="DSSAT")
    return "ok", 200

