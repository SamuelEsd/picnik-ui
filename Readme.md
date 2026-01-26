# Picnik UI

A web-based UI built with Streamlit for data analysis and visualization.

## Prerequisites

- **Python 3.13.0** (recommended)
- pip package manager

## Setup Instructions

### 1. Set Python Version

If you have a different Python version installed, use [pyenv](https://github.com/pyenv/pyenv):

```bash
pyenv install 3.13.0
pyenv local 3.13.0
```

### 2. Create Virtual Environment

```bash
python -m venv new_env
source new_env/bin/activate
```

### 3. Install Dependencies

```bash
sudo apt install python3-pip
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit web UI:

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

## Required Modules

- streamlit
- scipy
- seaborn
- picnik
- plotly

## Project Structure

- `main.py` - Main Streamlit application entry point
- `picnick_dev.py` - Development utilities
- `common/` - Shared utilities and helpers
- `views/` - UI page components
- `resources/` - Default data files and resources