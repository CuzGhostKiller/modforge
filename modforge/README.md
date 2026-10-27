
# ModForge

![ModForge Logo](https://via.placeholder.com/150x50/4A90E2/FFFFFF?text=ModForge)

**A powerful mod management tool for game mods**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/Tests-49%20passing-brightgreen.svg)](https://github.com/CuzGhostKiller/modforge)
[![GitHub Issues](https://img.shields.io/github/issues/CuzGhostKiller/modforge.svg)](https://github.com/CuzGhostKiller/modforge/issues)

## 🚀 Features

ModForge is a comprehensive mod management tool designed to help you organize, manage, and optimize your game mods with ease.

### Core Features

✅ **Mod Management**
- Add/remove mods from your library
- Enable/disable mods with one click
- Search and filter mods
- Discover mods from your game directories

✅ **Profile Management**
- Create multiple profiles for different game setups
- Switch between profiles instantly
- Duplicate and manage profiles
- Track mod states per profile

✅ **Load Order Management**
- Reorder mods with drag-and-drop or keyboard shortcuts
- Validate load order for conflicts
- Get load order recommendations
- Save and restore load orders

✅ **Data Persistence**
- Automatic save/load of your mod configurations
- Backup and restore functionality
- Data migration for future versions
- Cross-platform compatibility

## 📋 Installation

### Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)

### Installation Methods

#### Method 1: Using pip (Coming Soon)

```bash
pip install modforge
```

#### Method 2: From Source

```bash
# Clone the repository
git clone https://github.com/CuzGhostKiller/modforge.git
cd modforge

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run ModForge
python -m modforge
```

## 🛠️ Usage

### Command Line Interface

```bash
# Launch ModForge (GUI mode)
python -m modforge.main

# Run in headless mode (for scripting)
python -m modforge.main --headless

# Run with specific game directory
python -m modforge.main --game-dir "/path/to/your/game"
```

### GUI Interface

1. Launch ModForge
2. Go to Settings (File > Settings)
3. Configure your mod library directory and game directory
4. Enable headless mode if needed
5. Create profiles and organize your mods
6. Manage load order and enable/disable mods

### Headless Mode Features

When running in headless mode, ModForge provides basic information about your current setup:

```bash
$ python -m modforge.main --headless
Running in headless mode
Current profile: Default
Total mods: 42
Total profiles: 3
```

## 📁 Project Structure

```
modforge/
├── modforge/                # Main package
│   ├── core/                # Core functionality
│   │   ├── mod_manager.py   # Mod management
│   │   ├── profile_manager.py # Profile management
│   │   ├── load_order.py    # Load order management
│   │   └── persistence.py   # Data persistence
│   ├── gui/                 # GUI components
│   │   ├── main_window.py   # Main application window
│   │   ├── mod_list_view.py # Mod list view
│   │   ├── profile_view.py  # Profile view
│   │   └── widgets.py       # Reusable widgets
│   ├── models.py            # Data models
│   └── main.py              # Entry point
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python -m unittest tests.test_mod_manager

# Run with verbose output
python -m unittest tests -v
```

**Test Results**: 49 tests passing ✅

## 🎯 Roadmap

### Current Version: 0.1.0 (Alpha)

- [x] Core mod management
- [x] Profile management
- [x] Load order management
- [x] Data persistence
- [x] Unit test coverage
- [ ] GUI improvements
- [ ] Plugin system for game-specific rules
- [ ] Mod conflict detection
- [ ] Automatic load order optimization
- [ ] Mod update checker
- [ ] Cloud sync for profiles

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/modforge.git
cd modforge

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python tests/run_tests.py
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub:
[https://github.com/CuzGhostKiller/modforge/issues](https://github.com/CuzGhostKiller/modforge/issues)

## 🌟 Acknowledgments

- Thanks to all contributors and early testers
- Inspired by popular mod managers like Vortex and Mod Organizer
- Built with Python and PySide6 for cross-platform support

---

**ModForge - Organize Your Mods, Master Your Game!**

