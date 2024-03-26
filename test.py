import requests
import base64
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()


def send_file_to_server(file_path, url, totp_secret):
    try:
        totp = pyotp.TOTP(totp_secret)
        otp_token = totp.now()

        with open(file_path, "rb") as file:
            content_base64 = base64.b64encode(file.read()).decode("utf-8")

        headers = {"X-OTP": otp_token}
        data = {"filename": os.path.basename(file_path), "content": content_base64}
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    file_path = "v16m-default.akamaizead.mp4"
    url = "http://localhost:5000/write"
    totp_secret = os.getenv(
        "TOTP_SECRET"
    )  # Use the same TOTP secret as in your Flask app
    result = send_file_to_server(file_path, url, totp_secret)
    print(result)
