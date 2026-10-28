# ⚡ VoltVision — Smart Energy Microgrid Controller

**Team YAPGPT | HackSphere 3.0**

VoltVision is a machine-learning-based smart energy project that explores electricity-demand forecasting and microgrid decision support through a web dashboard.

🔗 **Live Demo:** [VoltVision Dashboard](https://project-rainfall-60093280894.development.catalystserverless.in)  
🔧 **Backend API:** [VoltVision API](https://voltvision-api-50047158633.development.catalystappsail.in)

---

## 📌 Problem Statement

Electricity demand varies with environmental conditions and usage patterns. Without effective forecasting and monitoring, managing demand and choosing appropriate energy sources can become difficult.

VoltVision explores how machine learning can estimate electricity demand and support decisions about grid operation.

## 💡 Our Solution

VoltVision combines a web dashboard, a Python backend, and machine-learning models to demonstrate:

- **Demand forecasting:** Estimate electricity demand using model inputs.
- **Forecast visualisation:** Display demand information through dashboard charts.
- **Grid decision support:** Apply predefined rules to recommend a grid mode.
- **Overload monitoring:** Flag demand values that exceed a configured threshold.

The project is a prototype for demonstrating these ideas, not a production-ready electricity-grid controller.

## ⚙️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn, Random Forest |
| Deployment | Zoho Catalyst |
| Data | CSV-based sample telemetry and model inputs |

## 🏗️ How It Works

```text
Sample Data and Environmental Inputs
                 |
                 v
      Machine-Learning Model
                 |
                 v
       Demand Prediction
                 |
                 v
       Grid Decision Rules
                 |
                 v
       VoltVision Dashboard
```

The model estimates demand, while the grid-decision component applies predefined rules to help interpret the result.

## 📊 Model Evaluation

The backend's metrics endpoint reported these demonstration results:

| Metric | Reported Value |
|---|---:|
| Mean Absolute Error (MAE) | 28.563 kW |
| Root Mean Squared Error (RMSE) | 37.504 kW |
| Rows Used | 4,000 |

These figures were reported from a random holdout split. They should not be interpreted as verified real-world forecasting accuracy. Further testing and validation are needed.

## 🌐 Deployed Endpoints

Base URL:

`https://voltvision-api-50047158633.development.catalystappsail.in`

| Endpoint | Purpose |
|---|---|
| `GET /` | Backend health and model information |
| `GET /metrics` | Model evaluation metrics |
| `GET /forecast/24h` | 24-hour forecast response |

The root and metrics endpoints were verified during development. The 24-hour forecast endpoint requires separate response validation before its output can be considered fully verified.

## 🚀 Run Locally

### Prerequisites

- Python installed
- Git installed
- A web browser

### 1. Clone the repository

```bash
git clone https://github.com/nidhiK78/VoltVision.git
cd VoltVision
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the backend

If `app.py` defines the FastAPI application as `app`, run:

```bash
uvicorn app:app --reload
```

The API should be available at `http://127.0.0.1:8000` while the local Uvicorn server is running.

To verify that the backend is responding, open `http://127.0.0.1:8000/` in your browser. If the connection is refused, check that the terminal running Uvicorn is still open and has no startup errors.

The deployed backend is available at:
https://voltvision-api-50047158633.development.catalystappsail.in/
### 5. Open the frontend

Open `frontend/index.html` in your browser.

Some frontend features may require the backend to be running and the API URL to be configured correctly. Check the existing application configuration if the dashboard does not load its data.

## 📁 Project Structure

```text
VoltVision/
├── backend/
│   └── controller.py
├── data/
│   └── sample_telemetry.csv
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── client-package.json
├── app.py
├── forecast.py
├── forecast_metrics.json
├── forecast_model.joblib
├── metrics.json
├── model.joblib
├── predict.py
├── requirements.txt
├── sample_test_input.csv
├── test_eval.py
├── train_forecast_model.py
└── train_model.py
```

## ⚠️ Limitations

- The reported model metrics are preliminary demonstration results.
- Real-world demand forecasting accuracy has not been established.
- Some dashboard visualisations may contain demonstration data.
- Grid recommendations are based on predefined rules and are not a substitute for professional grid-control systems.
- Production reliability and all deployed API responses have not been fully validated.

## 🔐 Security

- Never commit `.env` files, OAuth tokens, API keys, client secrets, or passwords.
- Configure credentials locally using environment variables.
- Review files before publishing changes to a public repository.

## 👥 Team

**YAPGPT — HackSphere 3.0**

VoltVision is a hackathon prototype exploring the use of machine learning for electricity-demand forecasting and microgrid decision support.
