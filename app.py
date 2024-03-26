from flask import Flask, request, jsonify, send_from_directory, abort
import os
import base64
import pyotp
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

FILES_FOLDER = "files"
os.makedirs(FILES_FOLDER, exist_ok=True)

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
    file_path = os.path.join(FILES_FOLDER, filename)
    with open(file_path, "wb") as file:
        file.write(content)
    return jsonify({"message": f"{filename} saved successfully."})


@app.route("/read/<filename>", methods=["GET"])
def read_file(filename):
    otp_token = request.headers.get("X-OTP")
    if not check_totp(otp_token):
        abort(403)
    file_path = os.path.join(FILES_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404
    return send_from_directory(FILES_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
