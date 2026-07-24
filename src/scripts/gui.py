"""GTK4 chat interface for the Mika chatbot.

Provides a native Linux GUI that follows the system theme, with message
timestamps, auto-scroll, and keyboard shortcuts.
"""

import datetime

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from src.scripts.chatbot_pkg import ChatBot
from src.scripts.config import APP_NAME, BOT_NAME


class ChatBotWindow(Gtk.ApplicationWindow):
    """Main chat window with message display, input field, and send button.

    Follows the system GTK theme (light/dark). Scrollable chat area
    with timestamps and auto-scroll on new messages.
    """

    def __init__(self, chatbot: ChatBot, app: Gtk.Application):
        """Initialize the chat window.

        Args:
            chatbot: The ChatBot instance to process messages.
            app: The parent GTK application.
        """
        super().__init__(application=app, title=APP_NAME)

        self.set_default_size(480, 640)
        self.chatbot = chatbot

        self._build_header()
        self._build_ui()
        self._apply_theme()

    def _build_header(self) -> None:
        """Create the header bar with app title."""
        header = Gtk.HeaderBar()
        self.set_titlebar(header)

    def _build_ui(self) -> None:
        """Build the main UI layout: chat area, input bar, send button."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.set_child(main_box)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        main_box.append(scrolled)

        self.chat_display = Gtk.TextView()
        self.chat_display.set_editable(False)
        self.chat_display.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.chat_display.set_left_margin(12)
        self.chat_display.set_right_margin(12)
        self.chat_display.set_top_margin(12)
        self.chat_display.set_bottom_margin(12)
        self.chat_display.set_cursor_visible(False)
        self.chat_buffer = self.chat_display.get_buffer()

        scrolled.set_child(self.chat_display)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(sep)

        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        input_box.set_margin_top(8)
        input_box.set_margin_bottom(8)
        input_box.set_margin_start(8)
        input_box.set_margin_end(8)

        main_box.append(input_box)

        self.input_field = Gtk.Entry()
        self.input_field.set_placeholder_text(f"Напиши сообщение {BOT_NAME}...")
        self.input_field.set_hexpand(True)
        self.input_field.connect("activate", self._on_enter_pressed)

        input_box.append(self.input_field)

        self.send_button = Gtk.Button(label="➤")
        self.send_button.set_size_request(60, -1)
        self.send_button.connect("clicked", self._on_send_clicked)

        input_box.append(self.send_button)

        self._append_system(
            f"Привет! Я {BOT_NAME}. Задай мне вопрос или просто поболтаем."
        )

    def _apply_theme(self) -> None:
        """Apply minimal CSS — only structural tweaks, colors come from the system theme."""
        css = Gtk.CssProvider()
        css.load_from_string(
            """
            textview {
                font-size: 14px;
            }

            entry {
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """
        )

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    @staticmethod
    def _timestamp() -> str:
        """Return a formatted current time string for message labels.

        Returns:
            Time string in HH:MM format.
        """
        return datetime.datetime.now(tz=datetime.UTC).astimezone().strftime("%H:%M")

    def _append_message(self, label: str, text: str, color: str) -> None:
        """Append a styled message to the chat buffer.

        Args:
            label: Sender label (e.g. "You:" or "Mika:").
            text: Message content.
            color: Pango markup color for the label.
        """
        end_iter = self.chat_buffer.get_end_iter()
        ts = self._timestamp()

        markup = (
            f'<span foreground="{color}" weight="bold">{label}</span> '
            f'<span foreground="#888888" size="small">{ts}</span>\n'
            f"{text}\n\n"
        )

        self.chat_buffer.insert_markup(end_iter, markup, -1)

        self.chat_buffer.place_cursor(self.chat_buffer.get_end_iter())
        self.chat_display.scroll_to_mark(
            self.chat_buffer.get_insert(), 0.0, False, 0.0, 0.0
        )

    def _append_system(self, text: str) -> None:
        """Append a system message (centered, dimmed).

        Args:
            text: System message text.
        """
        end_iter = self.chat_buffer.get_end_iter()
        markup = f'<span foreground="#666666" style="italic">{text}</span>\n\n'

        self.chat_buffer.insert_markup(end_iter, markup, -1)

    def _on_enter_pressed(self, _entry: Gtk.Entry) -> None:
        """Handle Enter key press in the input field."""
        self._handle_user_input()

    def _on_send_clicked(self, _button: Gtk.Button) -> None:
        """Handle Send button click."""
        self._handle_user_input()

    def _handle_user_input(self) -> None:
        """Process user input: display it, get bot response, display response."""
        user_text = self.input_field.get_text().strip()

        if not user_text:
            return

        self._append_message("You:", user_text, "#5dade2")
        self.input_field.set_text("")

        bot_response = self.chatbot.respond(user_text)

        self._append_message(f"{BOT_NAME}:", bot_response, "#a8d8ea")


def show_chatbot_interface(chatbot: ChatBot) -> None:
    """Launch the GTK4 chatbot interface.

    Creates a GtkApplication, connects the activate signal to
    create the main chat window, and starts the GTK event loop.

    Args:
        chatbot: Initialized ChatBot instance.
    """
    print("Launching chatbot GUI...")

    app = Gtk.Application(application_id="com.chatbot.mika")

    def on_activate(_app: Gtk.Application) -> None:
        window = ChatBotWindow(chatbot, _app)
        window.present()

    app.connect("activate", on_activate)
    app.run([])
