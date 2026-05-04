# Setup Guide - Assignment 18

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (for version control)

## Installation Steps

### 1. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Copy Configuration Template

```bash
cp .env.example .env
```

### 4. Edit Configuration (Optional)

For testing in simulator mode, no changes needed. For real hardware:

```bash
# Edit .env with your Azure credentials
notepad .env  # Windows
nano .env     # macOS/Linux
```

## Quick Start

### Run in Simulator Mode

```bash
# Default: uses simulators for all components
python app.py
```

### Run Tests

```bash
# Run all integration tests
python integration_test.py
```

### Run with Debug Logging

```bash
# More verbose output
LOG_LEVEL=DEBUG python app.py
```

## File Structure

```
Assignment_18/
├── app.py                 # Main orchestrator
├── proximity_monitor.py   # Distance sensor
├── camera_trigger.py      # Image capture
├── cloud_storage.py       # Azure Blob Storage
├── config.py              # Configuration manager
├── integration_test.py    # Test suite
├── requirements.txt       # Dependencies
├── .env.example           # Config template
├── .env                   # Your configuration (local)
├── .gitignore             # Git ignore rules
├── README.md              # Quick reference
├── SETUP.md               # This file
└── assignment18.md        # Full documentation
```

## Troubleshooting

### Module not found error
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Permission denied (macOS/Linux)
```bash
# Make scripts executable
chmod +x *.py
```

### Port already in use
```bash
# Use different port
export PORT=8001
python app.py
```

### Azure credentials not working
```bash
# Use simulator mode
SIMULATOR_MODE=true python app.py
```

## Next Steps

1. **Run tests:** `python integration_test.py`
2. **Check README.md:** Quick reference guide
3. **Read assignment18.md:** Full technical documentation
4. **Deploy to hardware:** Follow hardware setup in assignment18.md

## Support

For detailed information:
- See **assignment18.md** for technical details
- See **README.md** for quick reference
- Check `.env.example` for configuration options
