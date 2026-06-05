---
title: EstateIQ
emoji: house
colorFrom: yellow
colorTo: orange
sdk: docker
app_file: run.py
pinned: false
---

# EstateIQ - AI-Powered House Price Prediction

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/karishmaram-tech/EstateIQ)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange)](https://scikit-learn.org)

> **Live Demo:** https://huggingface.co/spaces/karishmaram-tech/EstateIQ

EstateIQ is a production-grade AI web application that predicts house prices instantly using a trained Gradient Boosting machine learning model. Built with a modular Flask backend, REST API, and a premium dark-themed frontend.

---

## Live Demo

Visit the live application: https://huggingface.co/spaces/karishmaram-tech/EstateIQ

---

## Features

- Real ML Model trained on 1,600 property records achieving 88.8% R2 accuracy
- SHAP Explainability showing feature importance for every prediction
- Blueprint Architecture with service layer separation
- Rate-limited REST API at /api/v1/predict with input validation
- Structured Logging with request IDs and response timing
- 71 Pytest Tests covering unit and integration levels
- GitHub Actions CI pipeline running on every push
- Dark and Light Mode with localStorage persistence
- Interactive Feature Impact Chart using Chart.js
- Docker deployment with Gunicorn

---

## Tech Stack

- Backend: Python 3.11, Flask 3.0, Blueprint Architecture
- ML: scikit-learn, Gradient Boosting Regressor, SHAP
- API: REST, Flask-Limiter, python-dotenv
- Frontend: HTML5, CSS3, Vanilla JavaScript, Chart.js
- Testing: pytest, pytest-flask, coverage
- DevOps: Docker, GitHub Actions, Hugging Face Spaces

---

## Model Performance

| Metric | Value |
|---|---|
| R2 Score | 88.8% |
| MAPE | 4.1% |
| RMSE | $22,000 |
| Cross-Validation | 85% (5-fold) |
| Training Records | 1,600 |
| Features | 10 |

---

## Project Structure 
EstateIQ/
├── app/
│   ├── init.py
│   ├── extensions.py
│   ├── routes/
│   │   ├── main.py
│   │   ├── prediction.py
│   │   └── health.py
│   └── services/
│       ├── predictor.py
│       └── validator.py
├── model/
│   ├── house_price_model.pkl
│   ├── metrics.json
│   └── shap_values.json
├── scripts/
│   └── train_model.py
├── tests/
├── templates/index.html
├── config.py
├── run.py
└── Dockerfile 
---

## API Reference

POST /api/v1/predict

Request body:
```json
{
  "area": 2100,
  "bedrooms": 4,
  "bathrooms": 3,
  "floors": 2,
  "year_built": 2005,
  "location_score": 7,
  "condition": 8,
  "garage": 1,
  "pool": 0,
  "garden": 1
}
```

Response:
```json
{
  "success": true,
  "price": 466676.00,
  "price_low": 429342.00,
  "price_high": 504011.00,
  "market_position": "Above Average",
  "response_time_ms": 45.2
}
```

---

## Local Setup

```bash
git clone https://github.com/karishmaram-tech/EstateIQ.git
cd EstateIQ
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open http://localhost:7860

---

## Run Tests

```bash
pytest -v
coverage run -m pytest && coverage report
```

---

## Author

Karishma Ram
- GitHub: https://github.com/karishmaram-tech
- LinkedIn: https://linkedin.com/in/karishmaram
- Live Demo: https://huggingface.co/spaces/karishmaram-tech/EstateIQ
