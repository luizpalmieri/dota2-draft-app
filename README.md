# Dota 2 Draft Analyzer

A comprehensive draft analysis tool for Dota 2 that provides strategic advice, item suggestions, and counter-tips based on hero selections.

## Project Structure

```
dota2-draft-app/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── core/                    # Core business logic
│   │   ├── __init__.py         # Core package exports
│   │   └── draft_analyzer_core.py  # Data management and analysis logic
│   └── ui/                      # User interface components
│       ├── __init__.py         # UI package exports
│       ├── custom_widgets.py   # Custom UI widgets
│       └── draft_analyzer_ui.py # Main application UI
├── data/                        # Game data files
│   ├── hero_images/            # Hero portrait images
│   ├── howdoiplay_json/        # Hero strategy data
│   ├── heroes.json             # Basic hero data
│   ├── normalized_heroes.json  # Normalized hero data
│   └── heroes.db               # Hero database
├── main.py                      # Application entry point
└── requirements.txt             # Python dependencies
```

## Features

- **Hero Selection Interface**: Autocomplete hero selection with images
- **Strategic Analysis**: Item suggestions and counter-tips
- **Comprehensive Data**: 120+ heroes with detailed strategy information

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Architecture

### Core Components

- **DataManager**: Handles loading and managing game data from JSON files
- **AnalysisCore**: Provides strategic analysis and recommendations
- **MainApplication**: Main UI controller and event handler

### Design Principles

- **Separation of Concerns**: Clear separation between UI, business logic, and data
- **Type Safety**: Full type annotations throughout the codebase
- **Modularity**: Well-organized package structure with proper imports
- **Error Handling**: Robust error handling and user feedback

## Development

The project follows Python best practices:
- PEP 8 style guidelines
- Type hints for all functions and methods
- Comprehensive docstrings
- Modular architecture with clear interfaces
