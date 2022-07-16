from flask import Flask, jsonify, request
from base64 import b64decode
from waitress import serve
from numpy import array
from io import BytesIO
from PIL import Image
import argparse
import time

from faceApp import faceEngine


app = Flask(__name__)
engine = faceEngine()
engine.init_feats()


response_code = {
    "ok": 200,
    "no_face": 422,
    "unauthenticated": 401,
    "unauthorized": 403,
    "bad_request": 400
    }


@app.route('/')
def index():
    return "<h1>Face Verification</h1>"


@app.route("/authentication", methods=["POST"])
def authentication():
    req = request.get_json()
    try:
        img = b64decode(req["img"])
        img = array(Image.open(BytesIO(img)).convert("RGB"))
    except:
       return {"message": "You send a bad request"}, response_code["bad_request"]

    tic = time.time()
    resp_obj = engine.authenticate(img)
    toc = time.time()
    resp_obj["seconds"] = round(toc-tic, 4)

    if resp_obj["name"] == "None":
        return {"message": "No face is detected"}, response_code["no_face"]
    elif resp_obj["authenticated"]:
        return jsonify({"name": resp_obj["name"]}), response_code["ok"]
    else:
        return {"message": "The user is unauthenticated"}, response_code["unauthenticated"]


@app.route('/authorization', methods=["POST"])
def authorization():
    req = request.get_json()
    try:
        img = b64decode(req["img"])
        img = array(Image.open(BytesIO(img)).convert("RGB"))
        uname = req["name"]
    except:
       return {"message": "You send a bad request"}, response_code["bad_request"]

    tic = time.time()
    resp_obj = engine.authorize(img, uname)
    toc = time.time()
    resp_obj["seconds"] = round(toc-tic, 4)

    if resp_obj["name"] == "None":
        return {"message": "No face is detected"}, response_code["no_face"]
    elif resp_obj["authorized"]:
        return {"message": "The user is authorized"}, response_code["ok"]
    else:
        return {"message": "The user is unauthorized"}, response_code["unauthorized"]


def create_app():
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', "--port", type=int,
                        default=5000, help="Port of serving api")
    args = parser.parse_args()
    # production server
    serve(app, host="0.0.0.0", port=args.port)
    # or in cmd: 
    #      waitress-serve --port=5000 --call api:create_app
    # development server
    # app.run(host='0.0.0.0', port=args.port)
