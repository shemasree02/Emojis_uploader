from flask import Flask, request, jsonify, send_from_directory
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

# Google Drive Setup
SERVICE_ACCOUNT_FILE = 'C:/Users/abhiv/OneDrive/Desktop/emojis_uploader/credentials.json'  # Adjust if needed
FOLDER_ID = '1zKY_b-pxcUPeEUnwN1M106aKDYMl1HaQ'  # Your Google Drive folder ID

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive.file']
)
drive_service = build('drive', 'v3', credentials=credentials)

@app.route("/")
def serve_home():
    return send_from_directory(app.static_folder, "emojis.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    try:
        file_stream = io.BytesIO(file.read())
        file_stream.seek(0)

        file_metadata = {
            'name': file.filename,
            'parents': [FOLDER_ID]
        }

        mimetype = file.mimetype or 'image/jpeg'
        media = MediaIoBaseUpload(file_stream, mimetype=mimetype)

        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return jsonify({
            "message": f"Image uploaded successfully to Google Drive! File ID: {uploaded_file.get('id')}"
        }), 200

    except Exception as e:
        return jsonify({"message": f"Upload failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
