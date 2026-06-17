# FoxConverter Web Engine

A modern React + FastAPI web application that reads raw FoxPro (`.DBF`) databases and serves dynamic, highly-accurate reports (Tax Registers, Stock Registers, Drill-down Vouchers).

## Setup Instructions

### 1. Backend Setup (Python)

You will need Python 3.8+ installed on your system.

```bash
# Clone the repository
git clone https://github.com/itsgoksz/Fox-converter-.git
cd Fox-converter-

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the required Python packages
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup (React/Node)

You will need Node.js (v18+) installed on your system. Open a **new terminal window** and navigate to the frontend folder:

```bash
cd frontend

# Install the Node packages
npm install

# Start the Vite development server
npm run dev
```

### 3. Usage
Once both servers are running, simply open the URL provided by Vite (usually `http://localhost:5173`) in your browser to access the FoxPro Hub!
