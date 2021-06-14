from app import app
from flask import send_from_directory, request, g, jsonify
import uuid
from config import Config
from app.helpers import save_request, save_response


### --- Routes of the honeypot websites --- ###

@app.route("/", methods=["GET", "POST"])
def index():
    return send_from_directory("static/fake-sites/web/", "index.html")


# Owncloud status page
@app.route("/stat")
@app.route("/status")
def status():
    d = {
        "installed": True,
        "maintenance": True,
        "needsDbUpgrade": True,
        "version": "8.1.7.2",
        "versionstring": "8.1.7",
        "edition": "Community",
        "productname": "Secure Cloud",
    }
    return jsonify(d)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:anypath>", methods=["GET", "POST"])
def catch_all(anypath):
    return send_from_directory("static/fake-sites/web/", "index.html")


@app.before_request
def before_request():
    # only save requests when path is not excluded from logging
    if request.path.startswith(tuple(Config.EXCLUDE_FROM_LOGGING)):
        g.log_response = False
        return
    g.log_response = True
    g.uuid = str(uuid.uuid4())
    save_request(g.uuid, request)


@app.after_request
def after_request(resp):
    # only save response when request was also saved
    if g.log_response is True:
        save_response(g.uuid, resp)
    return resp
