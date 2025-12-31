# airelav 📊

**An intelligent service for generating synthetic datasets based on natural language scenarios.**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-4FC08D.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
[![airelav CI/CD](https://github.com/ValeriiaEgorova/airelav/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ValeriiaEgorova/airelav/actions/workflows/ci-cd.yml)

## 📖 Overview

**airelav** is a web-based platform that eliminates the need to manually create test data or write generation scripts. Users simply describe the desired dataset in English or Russian (e.g., *"List of 500 bank transactions with outliers in amounts"*), and the system automatically generates a valid **CSV**, **Excel**, or **JSON** file.

The core technology uses **Google Gemini LLM** to interpret requirements and write Python code (Pandas/Faker), which is then executed in a secure, isolated **Docker Sandbox**.

## ✨ Key Features

*   **Natural Language Processing:** Converts text prompts into complex logic (dependencies, distributions, anomalies).
*   **Secure Execution:** All generated code runs inside ephemeral Docker containers (Sandboxes) with no network access.
*   **Self-Healing Mechanism:** If the AI generates buggy code, the system captures the error, feeds it back to the LLM, and automatically fixes the script.

## 🛠️ Tech Stack

### Backend
*   **Framework:** FastAPI (Python)
*   **Database:** PostgreSQL (via Docker Compose)
*   **ORM:** SQLModel (SQLAlchemy)
*   **AI Model:** Google Gemini 2.0 Flash (via `google-genai`)
*   **Security:** Passlib (Bcrypt), Python-JOSE (JWT)

### Frontend
*   **Framework:** Vue.js 3 (Composition API)
*   **Build Tool:** Vite
*   **Styling:** Tailwind CSS 3.4
*   **HTTP Client:** Axios

### Infrastructure
*   **Containerization:** Docker & Docker Compose
*   **Sandbox:** Custom Python Docker Image (`synthgen-env`)

## ⚙️ Prerequisites

Before running the project, ensure you have the following installed:
1.  **Python 3.10+**
2.  **Node.js** (LTS version)
3.  **Docker Desktop** (Must be running)
4.  **Git**

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/airelav.git
cd airelav
```

### 2. Backend Setup
Create a virtual environment and install dependencies:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and populate it with your keys:

```ini
# Google Gemini API Key (Get from https://aistudio.google.com/)
GEMINI_API_KEY="YOUR_GEMINI_KEY_HERE"
GEMINI_MODEL="gemini-2.0-flash"

# Security (Generate a random string: openssl rand -hex 32)
SECRET_KEY="your_super_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (PostgreSQL)
DB_USER=synth_user
DB_PASSWORD=synth_pass
DB_NAME=synthgen_db
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql://synth_user:synth_pass@localhost:5432/synthgen_db
```

### 4. Infrastructure Setup (Docker)
Start the PostgreSQL database and build the sandbox image:

```bash
# 1. Start Database
docker-compose up -d

# 2. Build the Sandbox Environment (Crucial Step!)
# This creates the image where Python code will run safely
docker build -t synthgen-env .
```

### 5. Frontend Setup
Open a new terminal window, go to the client folder:

```bash
cd client
npm install
```

## ▶️ Running the Application

You need two terminal windows running simultaneously.

**Terminal 1: Backend**
```bash
# Ensure venv is active
uvicorn main:app --reload
```
*The API will start at `http://127.0.0.1:8000`*

**Terminal 2: Frontend**
```bash
cd client
npm run dev
```
*The UI will start at `http://localhost:5173`*

## 👨‍💻 Development & Code Quality

We use strict code quality standards to ensure maintainability and reliability.

### 1. Install Development Dependencies
To install linters, formatters, and testing tools:

```bash
pip install -r requirements-dev.txt
```

### 2. Python (Backend) Quality Checks
We use **Ruff** (linter), **Black** (formatter), and **Mypy** (static typing).

```bash
# Format code automatically
black .

# Check for bugs and style issues
ruff check . --fix

# Check static types
mypy .
```

### 3. Vue.js (Frontend) Quality Checks
We use **ESLint** and **Prettier**.

```bash
cd client

# Check and fix issues
npm run lint

# Format code
npm run format
```

### 4. VS Code Setup (Recommended)
For the best experience, install these extensions:
- **Python** (Microsoft)
- **Ruff** (Charliermarsh)
- **ESLint** (Microsoft)
- **Prettier** (Esbenp)

The project is configured to **format on save** automatically.

## 📂 Project Structure

```text
synthgen-ai/
├── client/                 # Vue.js Frontend
│   ├── src/
│   │   ├── components/     # Login, Dashboard, etc.
│   │   ├── router/         # Vue Router config
│   │   └── App.vue
│   └── package.json
├── storage/                # Generated files (pkl, csv, xlsx)
├── auth.py                 # JWT & Hashing logic
├── core.py                 # AI Logic, Self-Healing, Docker execution
├── database.py             # Database connection
├── main.py                 # FastAPI endpoints
├── models.py               # SQLModel Database Schemas
├── Dockerfile              # Sandbox environment definition
├── docker-compose.yml      # PostgreSQL & Adminer config
└── requirements.txt        # Python dependencies
```

## 🧪 How to Use

1.  Open `http://localhost:5173`.
2.  **Register** a new account.
3.  In the Dashboard, enter a prompt.
    *   *Example:* "Generate a list of 100 employees with Name, Department, and Salary. Salary should be between 50k and 100k. 10% of emails should be missing."
4.  Click **Generate**.
5.  Wait for the progress bar to complete (Analysis -> Code Gen -> Docker Execution).
6.  Preview the data table and click **Download** (CSV/JSON/Excel).


## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
