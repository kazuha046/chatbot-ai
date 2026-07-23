# Chatbot AI - Mika

A Russian-language AI chatbot with three interfaces: GTK4 desktop GUI, web UI (Flask), and console mode. Built with TensorFlow/Keras, spaCy NLP, and NLTK.

## Features

- **Intent classification** using a neural network trained on custom patterns
- **Russian NLP** via spaCy (`ru_core_news_lg`) for lemmatization and named entity recognition
- **Weather** — real-time weather lookup via OpenWeatherMap API
- **Time** — current time reporting
- **Name memory** — remembers the user's name across sessions
- **Context tracking** — keeps a sliding window of the last 5 conversation turns
- **Confidence threshold** — gracefully handles unclear input instead of forcing a match
- **Three interfaces**: GTK4 GUI, Flask web app, terminal console

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- NixOS users: the included `flake.nix` provides all system dependencies (GTK4, spaCy, etc.)

## Quick Start

```bash
# Clone and enter the project
git clone https://github.com/kazuha046/chatbot-ai && cd chatbot-ai

# Install Python dependencies
uv sync

# (Optional) Create .env for weather support
echo 'WEATHER_API_KEY=your_key_here' > .env
# Get a free key at https://home.openweathermap.org/api_keys
```

## Usage

```bash
# GUI mode (default on most systems)
python main.py --gui

# Console mode
python main.py --no-gui

# Web mode (opens browser at localhost:5000)
python main.py --web

# Set default mode
python main.py --set-default gui
python main.py --set-default no-gui
python main.py --set-default web
```

### NixOS

```bash
nix develop     # enter dev shell (or direnv if configured)
uv sync
python main.py --gui
```

## Project Structure

```
chatbot-ai/
├── main.py                  # CLI entry point
├── src/
│   ├── scripts/
│   │   ├── chatbot.py       # Core ChatBot class (respond, predict, NER)
│   │   ├── model.py         # Keras model creation, training, caching
│   │   ├── preprocessing.py # Tokenization, lemmatization, bag-of-words
│   │   ├── config.py        # All constants, paths, style settings
│   │   ├── gui.py           # GTK4 desktop interface
│   │   ├── tools.py         # Launch helpers for each mode
│   │   ├── web.py           # Web mode launcher
│   │   ├── weather.py       # OpenWeatherMap integration
│   │   └── settings.py      # User settings and data persistence
│   ├── web/
│   │   ├── app.py           # Flask application
│   │   ├── templates/
│   │   │   └── index.html   # Web chat UI
│   │   └── static/
│   │       ├── styles.css
│   │       └── Onest.ttf
│   └── jsons/
│       ├── intents.json     # Training data (patterns + responses)
│       ├── settings.json
│       └── user.json
├── output/                  # Saved model + preprocessing artifacts
├── pyproject.toml
├── flake.nix                # Nix dev shell (GTK4, spaCy, etc.)
└── README.md
```

## How It Works

1. **Training** — Patterns from `intents.json` are tokenized and lemmatized with spaCy. A bag-of-words vocabulary is built. A 4-layer Keras neural network (512→256→128→N) is trained with batch normalization and dropout, using early stopping.
2. **Inference** — User input is converted to a bag-of-words vector, fed through the model. If the top prediction confidence is below `CONFIDENCE_THRESHOLD` (0.45), the bot returns a fallback "I don't understand" response.
3. **Special intents** — `weather`, `time`, `acquaintance`, and `user_name` tags trigger custom logic (API calls, datetime, spaCy NER, file I/O).

## Adding New Intents

Edit `src/jsons/intents.json` — add a new entry:

```json
{
  "tag": "my_intent",
  "patterns": ["pattern 1", "pattern 2"],
  "responses": ["Response 1", "Response 2"],
  "emoji": ["👍"]
}
```

Then delete `output/` and relaunch to retrain.

## Configuration

| Variable | Description | Default |
|---|---|---|
| `CONFIDENCE_THRESHOLD` | Minimum model confidence to accept a prediction | `0.45` |
| `MODEL_EPOCHS` | Max training epochs | `1000` |
| `MODEL_PATIENCE` | Early stopping patience (epochs) | `100` |
| `WEATHER_API_KEY` | OpenWeatherMap API key (in `.env`) | — |

## License

[MIT](LICENSE)
