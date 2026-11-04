from flask import Blueprint, current_app, jsonify, redirect, request

from . import db
from .utils import generate_code, is_valid_custom_code, is_valid_url

bp = Blueprint("links", __name__)

MAX_CODE_ATTEMPTS = 5


@bp.post("/api/shorten")
def shorten():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    custom = data.get("custom_code")
    db_path = current_app.config["DB_PATH"]

    if not is_valid_url(url):
        return jsonify(error="A valid http(s) URL is required."), 400

    if custom:
        if not is_valid_custom_code(custom):
            return jsonify(error="custom_code must be 3-32 chars: letters, digits, _ or -."), 400
        if not db.create_link(db_path, custom, url):
            return jsonify(error="That custom code is already taken."), 409
        code = custom
    else:
        for _ in range(MAX_CODE_ATTEMPTS):
            code = generate_code()
            if db.create_link(db_path, code, url):
                break
        else:
            return jsonify(error="Could not generate a unique code, try again."), 500

    return jsonify(code=code, short_url=request.host_url + code, url=url), 201


@bp.get("/<code>")
def follow(code: str):
    db_path = current_app.config["DB_PATH"]
    link = db.get_link(db_path, code)
    if link is None:
        return jsonify(error="Short link not found."), 404
    db.record_click(db_path, link["id"], request.headers.get("User-Agent"))
    return redirect(link["url"], code=302)


@bp.get("/api/stats/<code>")
def stats(code: str):
    result = db.get_stats(current_app.config["DB_PATH"], code)
    if result is None:
        return jsonify(error="Short link not found."), 404
    return jsonify(result)
