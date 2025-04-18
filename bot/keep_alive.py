from flask import Flask, request, jsonify
from threading import Thread
import requests

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/uptime-alert/', methods=['POST'])
def uptime_alert():
    print("✅ Received ping from Django")

    # Ping Django back
    try:
        django_ping_url = "https://discord-bot-logger-backend.onrender.com/discord-health/"  # Replace with your actual URL
        payload = {"from": "discord_bot", "status": "pong"}
        requests.post(django_ping_url, json=payload, timeout=3)
        print("↩️ Pinged back Django!")
    except Exception as e:
        print("❌ Failed to ping Django:", e)

    return jsonify({"status": "received"})

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
