# ⚡ Smart Energy Consumption Optimizer (HomeHostel)

An AI-powered web application that predicts electricity usage and recommends optimized energy-saving schedules for homes and hostels.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000?style=flat-square&logo=flask)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat-square&logo=chartdotjs&logoColor=white)

---

## 🎯 Features

- **AI-Powered Prediction** — Random Forest ML model predicts daily/monthly energy consumption
- **Optimization Engine** — Rule-based + heuristic algorithms generate energy-saving schedules
- **Savings Calculator** — Before vs after comparison with ₹ cost estimation (Indian tariff slabs)
- **Interactive Dashboard** — Chart.js visualizations: breakdown, trends, comparisons
- **Simulation Mode** — Test scenarios: weekends, summer, winter, work-from-home
- **Dark/Light Theme** — Premium glassmorphism UI with smooth transitions
- **PDF Export** — Generate printable energy reports
- **Efficiency Rating** — A+ to D grade based on optimization potential

---

## 🛠️ Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| **Frontend**  | HTML5, CSS3 (Glassmorphism), JS     |
| **Backend**   | Python, Flask, Flask-CORS           |
| **ML/AI**     | Scikit-learn, Pandas, NumPy         |
| **Charts**    | Chart.js 4.4                        |
| **Font**      | Google Fonts (Inter)                |

---

## 📁 Project Structure

```
Smart Energy Consumption Optimizer/
├── backend/
│   ├── app.py              # Flask server + API endpoints
│   ├── predictor.py         # ML model loader + prediction logic
│   ├── optimizer.py         # Optimization engine + scheduling
│   └── __init__.py
├── frontend/
│   ├── index.html           # Main SPA page
│   ├── css/
│   │   └── styles.css       # Design system (dark/light mode)
│   └── js/
│       ├── app.js           # Application logic + API calls
│       └── charts.js        # Chart.js visualization module
├── model/
│   ├── train_model.py       # ML model training script
│   ├── energy_model.pkl     # Trained model (auto-generated)
│   └── model_metrics.json   # Training metrics (auto-generated)
├── data/
│   ├── generate_dataset.py  # Synthetic data generator
│   └── energy_data.csv      # Training dataset (auto-generated)
├── run.py                   # Single entry point
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step-by-Step Setup

```bash
# 1. Clone/navigate to the project
cd "Smart Energy Consumption Optimizer"

# 2. (Optional) Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application (auto-generates data + trains model + starts server)
python run.py
```

### Open in Browser
```
http://localhost:5000
```

---

## 📊 API Endpoints

| Method | Endpoint           | Description                          |
|--------|--------------------|--------------------------------------|
| GET    | `/`                | Serve frontend                       |
| GET    | `/api/appliances`  | Get supported appliances + wattages  |
| GET    | `/api/model-info`  | Get ML model performance metrics     |
| POST   | `/api/predict`     | Predict energy consumption           |
| POST   | `/api/optimize`    | Generate optimization schedule       |
| POST   | `/api/simulate`    | Run scenario simulations             |

---

## 🤖 ML Model Details

- **Algorithm**: Random Forest Regressor (100 trees)
- **Features**: rooms, occupants, appliance count, usage hours, temperature, AC flag, heavy appliance flag
- **Target**: Daily energy consumption (kWh)
- **Training Data**: 2000 synthetic samples based on Indian household patterns
- **Evaluation**: MAE, RMSE, R² score

---

## ☁️ Deployment

### Render (Recommended)
1. Push to GitHub
2. Create a new Web Service on [render.com](https://render.com)
3. Set:
   - **Build Command**: `pip install -r requirements.txt && python -c "from data.generate_dataset import generate_dataset; generate_dataset()" && python -c "from model.train_model import train_model; train_model()"`
   - **Start Command**: `python run.py`
   - **Environment Variable**: `PORT=10000`

### Vercel (Frontend only)
1. Deploy the `frontend/` folder to Vercel
2. Host the backend separately on Render

---

## 📋 Usage Guide

1. **Input Panel** — Set rooms, occupants, temperature, and configure appliances
2. **Predict** — Click "Predict Energy Usage" to get AI-powered consumption estimates
3. **Optimize** — Click "Optimize & Save Energy" for personalized recommendations
4. **Dashboard** — Run scenario simulations to compare usage across situations
5. **Export** — Generate a PDF report of your analysis

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for smarter energy consumption
</p>
