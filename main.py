import argparse
import sys

from dotenv import load_dotenv

from src.scripts.settings import load_setting, save_setting
from src.scripts.tools import start_bot, start_bot_gui, start_bot_web

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(prog="mika")

    parser.add_argument("--no-gui", action="store_true", help="Run in console mode")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")
    parser.add_argument("--web", action="store_true", help="Run in web mode")
    parser.add_argument(
        "--set-default",
        choices=["gui", "no-gui", "web"],
        help="Set default interface mode",
    )

    args = parser.parse_args()

    if args.set_default:
        save_setting(args.set_default, "mode")
        print(f"Default mode set to: {args.set_default}")
        sys.exit(0)

    setting = load_setting()

    if args.no_gui:
        start_bot()
    elif args.web:
        start_bot_web()
    elif args.gui:
        start_bot_gui()
    elif setting and setting.get("mode") == "no-gui":
        start_bot()
    elif setting and setting.get("mode") == "web":
        start_bot_web()
    elif setting and setting.get("mode") == "gui":
        start_bot_gui()
    else:
        sys.exit(
            f"Invalid default interface mode: {setting}. "
            f"Use --set-default <mode> to set a new default. "
            f"Available modes: gui, no-gui, web"
        )
