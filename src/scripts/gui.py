import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from src.scripts.chatbot import ChatBot
from src.scripts.config import *


class ChatBotInterface(Gtk.ApplicationWindow):
    def __init__(self, chatbot, app):
        super().__init__(application=app, title=APP_NAME)

        self.set_default_size(400, 500)
        self.chatbot = chatbot

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.set_margin_top(6)
        main_box.set_margin_bottom(6)
        main_box.set_margin_start(6)
        main_box.set_margin_end(6)
        self.set_child(main_box)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        self.chat_display = Gtk.TextView()
        self.chat_display.set_editable(False)
        self.chat_display.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.chat_display.set_left_margin(10)
        self.chat_display.set_right_margin(10)
        self.chat_display.set_top_margin(10)
        self.chat_display.set_bottom_margin(10)
        self.chat_buffer = self.chat_display.get_buffer()
        scrolled.set_child(self.chat_display)

        self.input_field = Gtk.Entry()
        self.input_field.set_placeholder_text("Type your message...")
        self.input_field.set_hexpand(True)
        self.input_field.connect("activate", self.on_enter_pressed)
        main_box.append(self.input_field)

        self.send_button = Gtk.Button(label="Send")
        self.send_button.add_css_class("suggested-action")
        self.send_button.connect("clicked", self.on_send_clicked)
        main_box.append(self.send_button)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(
            f"""
            textview {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
                font-size: {FONT_SIZE};
                border: 1px solid {BORDER_COLOR};
                border-radius: {BORDER_RADIUS};
            }}

            textview text {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}

            entry {{
                padding: {INPUT_FIELD_PADDING};
                font-size: {FONT_SIZE};
                border: 1px solid {INPUT_FIELD_BORDER_COLOR};
                border-radius: {BORDER_RADIUS};
            }}

            button {{
                background-color: {SEND_BUTTON_BACKGROUND};
                color: {TEXT_COLOR};
                padding: {SEND_BUTTON_PADDING};
                font-size: {FONT_SIZE};
                border-radius: {BORDER_RADIUS};
            }}

            scrollbar {{
                background: {SCROLLBAR_BACKGROUND};
                border-radius: {BORDER_RADIUS};
            }}

            scrollbar slider {{
                background: {SCROLLBAR_HANDLE};
                border-radius: {BORDER_RADIUS};
                min-width: {SCROLLBAR_WIDTH};
            }}
        """
        )

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def append_chat_message(self, label, text):
        end_iter = self.chat_buffer.get_end_iter()
        self.chat_buffer.insert_markup(end_iter, f"<b>{label}</b> {text}\n", -1)

    def on_enter_pressed(self):
        self.handle_user_input()

    def on_send_clicked(self):
        self.handle_user_input()

    def handle_user_input(self):
        user_text = self.input_field.get_text().strip()

        if user_text:
            self.append_chat_message("You:", user_text)

            bot_response = self.chatbot.respond(user_text)

            self.append_chat_message("Bot:", bot_response)
            self.input_field.set_text("")


def show_chatbot_interface(chatbot: ChatBot):
    print("Launching chatbot GUI...")

    app = Gtk.Application(application_id="com.chatbot.mika")

    def on_activate(_app):
        window = ChatBotInterface(chatbot, _app)
        window.present()

    app.connect("activate", on_activate)
    app.run([])
