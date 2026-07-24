"""Entry points for launching the chatbot in different modes.

Provides functions to start the bot in console, GTK4 GUI, or web interface.
"""

from src.scripts.chatbot_pkg import ChatBot
from src.scripts.gui import show_chatbot_interface
from src.scripts.web import open_chatbot_web


def start_bot_web():
    """Starts the chatbot in web mode."""
    print("Starting chatbot in web mode...")
    open_chatbot_web()


def start_bot_gui():
    """Starts the chatbot in GUI mode."""
    print("Starting chatbot in GUI mode...")

    chatbot = ChatBot()
    show_chatbot_interface(chatbot)


def start_bot():
    """Starts the chatbot in console mode."""
    print("Starting chatbot in console mode. Type 'exit' to quit.")
    chatbot = ChatBot()

    while True:
        user_input = input("You: ")

        if not user_input:
            print("Please enter a message.")
            continue

        if user_input.lower() in ("exit", "quit", "выход"):
            break

        bot_response = chatbot.respond(user_input)
        print(f"Bot: {bot_response}")
