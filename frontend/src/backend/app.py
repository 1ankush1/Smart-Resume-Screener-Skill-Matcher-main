"""Purpose: Creates the public Flask API and serves the built frontend."""

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from routes.matching import matching_bp


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

    app.register_blueprint(matching_bp, url_prefix="/api/matching")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    frontend_dist = Path(os.getenv(
        "FRONTEND_DIST_DIR",
        str(Path(__file__).resolve().parents[2] / "dist"),
    ))

    @app.get("/")
    def frontend_home():
        if (frontend_dist / "index.html").is_file():
            return send_from_directory(frontend_dist, "index.html")
        return jsonify({"error": "Frontend build not found."}), 404

    @app.route("/api/<path:api_path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def unknown_api_endpoint(api_path):
        return jsonify({"error": "API endpoint not found."}), 404

    @app.get("/<path:frontend_path>")
    def frontend_routes(frontend_path):
        if frontend_path.startswith("api/"):
            return jsonify({"error": "API endpoint not found."}), 404
        target = frontend_dist / frontend_path
        if target.is_file():
            return send_from_directory(frontend_dist, frontend_path)
        if (frontend_dist / "index.html").is_file():
            return send_from_directory(frontend_dist, "index.html")
        return jsonify({"error": "Frontend build not found."}), 404

    @app.errorhandler(Exception)
    def unexpected_error(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("Unhandled request error: %s %s", request.method, request.path)
        return jsonify({"error": "An unexpected server error occurred."}), 500

    @app.errorhandler(413)
    def file_too_large(_error):
        return jsonify({"error": "File is too large. Maximum size is 5 MB."}), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").strip().lower() == "true",
    )
