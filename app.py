from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import io
import base64
import requests
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Read the DataFrame from the uploaded file
        df = pd.read_csv(file)
        
        # Serialize the DataFrame to bytes using joblib
        buffer = io.BytesIO()
        joblib.dump(df, buffer)
        df_bytes = buffer.getvalue()

        # Encode the bytes to base64
        df_base64 = base64.b64encode(df_bytes).decode('utf-8')

        return jsonify({'dataframe': df_base64}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy_post', methods=['POST'])
def proxy_post():
    data = request.json
    try:
        response = requests.post(
            'https://chat2plot.azurewebsites.net/api/httptrigger1?code=0XEttLdbkBrUWJnHeToLisiYdvXlvTcCVpN9Uxu7KuauAzFuk_anPQ%3D%3D',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        logging.info(f"Azure POST response: {response.json()}")  # Log the response
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logging.error(f"Error in proxy_post: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/proxy_get', methods=['GET'])
def proxy_get():
    try:
        input_query = request.args.get('input')
        chart_format = request.args.get('chart_format')

        response = requests.get(
            'https://chat2plot.azurewebsites.net/api/httptrigger1?code=0XEttLdbkBrUWJnHeToLisiYdvXlvTcCVpN9Uxu7KuauAzFuk_anPQ%3D%3D',
            json={
                'input': input_query,
                'chart_format': chart_format
            }
        )
        logging.info(f"Azure GET response: {response.json()}")  # Log the response
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to retrieve data from Azure endpoint'}), response.status_code

    except Exception as e:
        logging.error(f"Error in proxy_get: {e}")
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

