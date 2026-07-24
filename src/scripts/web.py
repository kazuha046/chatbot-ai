"""Web server launcher for the Flask-based chatbot interface.

Starts the Flask development server and opens the chat UI in a browser.
"""

import threading
import webbrowser

from src.web.app import app


def open_chatbot_web() -> None:
    """Start the Flask server and open the chat interface in a browser.

    Launches the server on http://127.0.0.1:5000 and opens a browser
    tab after a 1-second delay to allow the server to start.
    """
    threading.Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False)
