from flask import Flask, render_template, request, redirect, url_for, jsonify
import datetime
import requests

app = Flask(__name__)

# Configuration for Pocketbase
POCKETBASE_URL = "http://127.0.0.1:8090"  # Default Pocketbase URL
COLLECTION_NAME = "messages"

@app.route('/')
def index():
    now = datetime.datetime.now()
    day_of_week = now.strftime("%A")
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    return render_template('index.html', day_of_week=day_of_week, date=date, time=time)

@app.route('/latest_message')
def latest_message():
    try:
        response = requests.get(f"{POCKETBASE_URL}/api/collections/{COLLECTION_NAME}/records?sort=-created&perPage=1")
        response.raise_for_status()
        data = response.json()
        latest_message = data['items'][0]['text'] if data['items'] else ""
        return jsonify({'message': latest_message})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error fetching message: {e}"}), 500

@app.route('/input')
def input_page():
    return render_template('input.html')

@app.route('/submit', methods=['POST'])
def submit_text():
    text = request.form.get('text')
    if text and len(text) <= 255:
        try:
            data = {"text": text}
            response = requests.post(f"{POCKETBASE_URL}/api/collections/{COLLECTION_NAME}/records", json=data)
            response.raise_for_status()
            return redirect(url_for('index'))
        except requests.exceptions.RequestException as e:
            return f"Error submitting message: {e}"
    else:
        return "Text cannot be empty or exceed 255 characters."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
