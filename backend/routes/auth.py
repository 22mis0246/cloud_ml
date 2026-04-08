from pathlib import Path
from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, LoginLog, SecurityAlert
import joblib
import pandas as pd

auth = Blueprint("auth", __name__)
MODEL_DIR = Path(__file__).resolve().parent.parent


def infer_device_type(device_full):
    mobile_tokens = ("Mobile", "Android", "iPhone", "iPad")
    return "Mobile" if any(token in device_full for token in mobile_tokens) else "Desktop"


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        raw_password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username already exists. Try another one.", "warning")
            return redirect(url_for("auth.register"))

        password = generate_password_hash(raw_password)

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. You can log in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

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

            device_type = infer_device_type(device_full)
            

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

                session["user_id"] = user.id
                flash("Learning mode active. Login approved and behavior recorded.", "info")
                return redirect(url_for("dashboard.home"))

            # ------------------------
            # Run Anomaly Detection
            # ------------------------
            try:
                model = joblib.load(MODEL_DIR / "anomaly_model.pkl")
                le_ip = joblib.load(MODEL_DIR / "ip_encoder.pkl")
                le_device = joblib.load(MODEL_DIR / "device_encoder.pkl")
                scaler = joblib.load(MODEL_DIR / "scaler.pkl")
            except Exception:
                flash("Security model not found. Train the model before checking advanced risk.", "danger")
                return redirect(url_for("auth.login"))

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
                alert = SecurityAlert(
                    user_id=user.id,
                    title="Suspicious login attempt blocked",
                    message=(
                        f"We blocked an unusual login attempt for {user.username}. "
                        f"Review the source IP and device fingerprint before trusting it."
                    ),
                    risk_level="critical",
                    source_ip=ip,
                    ip_group=ip_group,
                    device_type=device_type,
                    login_hour=login_hour,
                )
                db.session.add(alert)
                db.session.commit()
                session.clear()
                return render_template(
                    "alert_blocked.html",
                    username=user.username,
                    attempted_at=now.strftime("%d %b %Y, %I:%M %p"),
                    source_ip=ip,
                    ip_group=ip_group,
                    device_type=device_type,
                    login_hour=login_hour,
                )

            # If normal login
            db.session.add(log)
            db.session.commit()

            session["user_id"] = user.id
            flash("Identity verified. Access granted.", "success")
            return redirect(url_for("dashboard.home"))

        else:
            flash("Invalid credentials. Check your username and password.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("Session closed.", "info")
    return redirect(url_for("auth.login"))
