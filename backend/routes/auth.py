from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, LoginLog
import joblib
import pandas as pd

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id

            # ------------------------
            # Feature Extraction
            # ------------------------
            now = datetime.now()
            day_of_week = now.weekday()

            ip = request.remote_addr or "0.0.0.0"
            ip_parts = ip.split(".")
            device_full = request.user_agent.string

            # ====================================================
            # 🔥 TEMPORARY LOGIN SIMULATION FOR LOCALHOST TESTING
            # ====================================================
            # This block simulates user-specific normal behavior
            # Comment this block when switching to real extraction

            """"
            if user.id == 1:
                login_hour = 12
                ip_group = "120.45"
                device_type = "Desktop"

            elif user.id == 2:
                login_hour = 21
                ip_group = "150.20"
                device_type = "Mobile"

            elif user.id == 3:
                login_hour = 10
                ip_group = "175.60"
                device_type = "Desktop"

            else:
                login_hour = now.hour
                ip_group = ".".join(ip_parts[:2])
                device_type = "Desktop"
            """

            # ====================================================
            # 🔁 ORIGINAL REAL FEATURE EXTRACTION (COMMENTED)
            # ====================================================
            # Uncomment this section and remove simulation block
            # when moving to real deployment

            
            login_hour = now.hour
            ip_group = ".".join(ip_parts[:2]) if len(ip_parts) >= 2 else ip

            if "Mobile" in device_full:
                device_type = "Mobile"
            else:
                device_type = "Desktop"
            

            # ------------------------
            # Prepare login log object
            # ------------------------
            log = LoginLog(
                user_id=user.id,
                login_time=now,
                login_hour=login_hour,
                day_of_week=day_of_week,
                ip_address=ip,
                ip_group=ip_group,
                device_full=device_full,
                device_type=device_type
            )

            # ------------------------
            # Grace Period Check
            # ------------------------
            login_count = LoginLog.query.filter_by(user_id=user.id).count()

            if login_count < 5:
                print("Learning phase - skipping anomaly detection")

                db.session.add(log)
                db.session.commit()

                return redirect("/dashboard")

            # ------------------------
            # Run Anomaly Detection
            # ------------------------
            try:
                model = joblib.load("anomaly_model.pkl")
                le_ip = joblib.load("ip_encoder.pkl")
                le_device = joblib.load("device_encoder.pkl")
                scaler = joblib.load("scaler.pkl")
            except:
                return "Model not found. Train model first."

            # Encode categorical features
            try:
                ip_encoded = le_ip.transform([ip_group])[0]
            except:
                ip_encoded = -1

            try:
                device_encoded = le_device.transform([device_type])[0]
            except:
                device_encoded = -1

            # Create DataFrame
            features = pd.DataFrame([{
                "user_id": user.id,
                "login_hour": login_hour,
                "ip_group_encoded": ip_encoded,
                "device_encoded": device_encoded
            }])

            features_scaled = scaler.transform(features)

            prediction = model.predict(features_scaled)[0]

            print("Features:", features)
            print("Scaled:", features_scaled)
            print("Prediction:", prediction)

            if prediction == -1:
                return "🚨 Suspicious login detected! Access denied."

            # If normal login
            db.session.add(log)
            db.session.commit()

            return redirect("/dashboard")

        else:
            return "Invalid credentials"

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")