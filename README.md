# Train Scrabble

This project is a Scrabble training program that helps users practice specific words.

## Project Structure

```
train_scrabble/
├── data/           # Contains word lists and game data
├── src/            # Source code
│   ├── models/     # Core data structures
│   ├── modules/    # Game logic modules
│   ├── services/   # Game services
│   └── utils/      # Utility functions
└── tests/          # Unit tests
```

## Setup and Running

To run this project correctly, you need to ensure Python can find the src package. There are two ways to do this:

1. Using Python module mode (recommended):
```bash
# From the project root directory:
python -m src.main
```

2. By adding the project root to PYTHONPATH:
```bash
# On Windows:
set PYTHONPATH=%PYTHONPATH%;.
python src/main.py

# On Unix/Linux/MacOS:
export PYTHONPATH=$PYTHONPATH:.
python src/main.py
```

## Development

When running tests or working on the code, make sure to use one of the methods above to ensure proper module imports.