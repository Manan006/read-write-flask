from flask import Flask, request, jsonify, send_from_directory, abort
import os
import base64
import pyotp
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

READ_FOLDER = "/workspace/ComfyUI/output"
WRITE_FOLDER = "/workspace/ComfyUI/input"

os.makedirs(READ_FOLDER, exist_ok=True)
os.makedirs(WRITE_FOLDER, exist_ok=True)

TOTP_SECRET = os.getenv("TOTP_SECRET")


def check_totp(token):
    totp = pyotp.TOTP(TOTP_SECRET)
    return totp.verify(token)


@app.route("/write", methods=["POST"])
def write_file():
    otp_token = request.headers.get("X-OTP")
    if not check_totp(otp_token):
        abort(403)
    data = request.json
    filename = data.get("filename")
    content_base64 = data.get("content")
    if not filename or not content_base64:
        return jsonify({"message": "Filename and content are required"}), 400
    content = base64.b64decode(content_base64)
    file_path = os.path.join(WRITE_FOLDER, filename)
    with open(file_path, "wb") as file:
        file.write(content)
    return jsonify({"message": f"{filename} saved successfully."})


@app.route("/read/<filename>", methods=["GET"])
def read_file(filename):
    otp_token = request.headers.get("X-OTP")
    if not check_totp(otp_token):
        abort(403)
    file_path = os.path.join(READ_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404
    return send_from_directory(READ_FOLDER, filename)


@app.route("/check-ready", methods=["GET"])
def check_ready():
    ready = os.path.exists("/tmp/start-script-over")
    if ready:
        return jsonify({"status": True, "message": "ready"}), 200
    else:
        return jsonify({"status": False, "message": "not ready"}), 200


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
