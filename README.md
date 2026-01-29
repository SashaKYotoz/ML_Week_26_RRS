# ☕ 1-212-12 group RRS

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Axios](https://img.shields.io/badge/Frontend-Axios-orange.svg)](https://axios-http.com/docs/intro)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
<br>
## Repository Structure

The project is organized into following pattern:

```text
├── backend                # Backend operations over user request to model prediction
│   ├── main.py            # Operates front to back -end requests
│   ├── recommendations.py # Outputs recommendations list in json format based on model answer
│   ├── schemas.py         # Schema of pydantic model 
│   └── twotower.py        # Presents working model of current system
├── front/                 # User interface
├── experiments/           # Operations under dataset for the filtering with little to no machine learning
├── temp/                  # Filtering and analyzing classes released for conceptualization
├── requirements.txt       # Project python dependencies
└── README.md              # Project documentation
```

## 🚀 Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/SashaKYotoz/ML_Week_26_RRS.git
cd ML_Week_26_RRS
```
### 2. Setup environment

```bash
# Create a virtual environment to isolate dependencies
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate 
# On Windows:
venv\Scripts\activate

# Install all necessary libraries from requirements.txt
pip install -r requirements.txt
```
### 3. Running the Application

To start the full system, you need to run the backend server, open index.html to graphical output.
```
uvicorn main:app --app-dir backend --host 0.0.0.0 --port 80
```

### 3.1. Start the Backend Server
The server handles API requests and model inference. Navigate to the project root and run:
```bash
http://localhost/
```
### 3.2. Frontend Interface
Frontend is represented as basic html-js app where index.html is graphic interface of this project. Inputs on html are processed via script.js with get request operated by axios javascript library and once response is received cards of recommended coffees are generated.
