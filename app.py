"""
House Price Prediction - Flask Application
==========================================
Main entry point for the web app.
Run with: python app.py
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
import joblib
import os

app = Flask(__name__)

# -------------------------------------------------------
# Load your trained model (update path if needed)
# -------------------------------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "house_price_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
except FileNotFoundError:
    MODEL_LOADED = False
    print(f"[WARNING] Model not found at {MODEL_PATH}. Using mock predictions.")

# -------------------------------------------------------
# Model performance metrics — update with your real values
# -------------------------------------------------------
MODEL_METRICS = {
    "r2_score":   0.89,
    "mae":        18500,
    "rmse":       24300,
    "accuracy":   89,
    "train_size": 15480,
    "features":   13,
}

# -------------------------------------------------------
# Feature order must match what the model was trained on
# -------------------------------------------------------
FEATURE_ORDER = [
    "area", "bedrooms", "bathrooms", "stories",
    "mainroad", "guestroom", "basement", "hotwaterheating",
    "airconditioning", "parking", "prefarea", "furnishingstatus_semi",
    "furnishingstatus_unfurnished",
]


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html", metrics=MODEL_METRICS)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accept JSON form data, run the model, return a prediction.
    Expected JSON keys match FEATURE_ORDER above.
    """
    try:
        data = request.get_json(force=True)

        # --- parse inputs ---
        area               = float(data.get("area", 0))
        bedrooms           = int(data.get("bedrooms", 1))
        bathrooms          = int(data.get("bathrooms", 1))
        stories            = int(data.get("stories", 1))
        mainroad           = 1 if data.get("mainroad") == "yes" else 0
        guestroom          = 1 if data.get("guestroom") == "yes" else 0
        basement           = 1 if data.get("basement") == "yes" else 0
        hotwaterheating    = 1 if data.get("hotwaterheating") == "yes" else 0
        airconditioning    = 1 if data.get("airconditioning") == "yes" else 0
        parking            = int(data.get("parking", 0))
        prefarea           = 1 if data.get("prefarea") == "yes" else 0
        furnishing         = data.get("furnishingstatus", "furnished")
        semi_furnished     = 1 if furnishing == "semi-furnished" else 0
        unfurnished        = 1 if furnishing == "unfurnished" else 0

        features = np.array([[
            area, bedrooms, bathrooms, stories,
            mainroad, guestroom, basement, hotwaterheating,
            airconditioning, parking, prefarea,
            semi_furnished, unfurnished,
        ]])

        if MODEL_LOADED:
            price = float(model.predict(features)[0])
        else:
            # Mock formula when no model file is present
            price = (
                area * 120
                + bedrooms * 50000
                + bathrooms * 40000
                + stories * 30000
                + mainroad * 80000
                + airconditioning * 60000
                + parking * 20000
                + 200000
            )

        # Build a simple price range (±8 %)
        low  = price * 0.92
        high = price * 1.08

        # Price-per-sqft
        ppsf = price / area if area > 0 else 0

        return jsonify({
            "success":    True,
            "price":      round(price),
            "price_low":  round(low),
            "price_high": round(high),
            "price_sqft": round(ppsf, 2),
            "confidence": 89,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    # Hugging Face Spaces uses port 7860 by default
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
