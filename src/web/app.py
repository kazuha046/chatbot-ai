from flask import Flask, request, jsonify, render_template
from src.scripts.chatbot import ChatBot

app = Flask(__name__)
chatbot = ChatBot()


@app.route("/")
def index():
    """Renders the main chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handles chat messages and returns bot responses."""
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    bot_response = chatbot.respond(user_message)

    return jsonify({"response": bot_response})
