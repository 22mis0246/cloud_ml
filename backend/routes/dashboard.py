from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import db, User, LoginLog, SecurityAlert

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
def home():
    if "user_id" not in session:
        return redirect("/login")

    user = db.session.get(User, session["user_id"])
    if user is None:
        session.clear()
        return redirect("/login")

    alerts = (
        SecurityAlert.query
        .filter_by(user_id=user.id)
        .order_by(SecurityAlert.created_at.desc())
        .all()
    )
    unseen_alerts = [alert for alert in alerts if not alert.seen]
    if unseen_alerts:
        for alert in unseen_alerts:
            alert.seen = True
        db.session.commit()

    recent_logs = (
        LoginLog.query
        .filter_by(user_id=user.id)
        .order_by(LoginLog.login_time.desc())
        .limit(6)
        .all()
    )

    active_alerts = [alert for alert in alerts if not alert.acknowledged]
    trusted_devices = len({log.device_type for log in recent_logs if log.device_type})
    last_login = recent_logs[0] if recent_logs else None

    return render_template(
        "dashboard.html",
        user=user,
        alerts=alerts,
        active_alerts=active_alerts,
        recent_logs=recent_logs,
        trusted_devices=trusted_devices,
        total_logins=LoginLog.query.filter_by(user_id=user.id).count(),
        last_login=last_login,
    )


@dashboard.route("/alerts/<int:alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    if "user_id" not in session:
        return redirect("/login")

    alert = db.session.get(SecurityAlert, alert_id)
    if alert is None or alert.user_id != session["user_id"]:
        flash("That security alert was not found for your account.", "warning")
        return redirect(url_for("dashboard.home"))

    alert.acknowledged = True
    alert.seen = True
    db.session.commit()
    flash("Security alert acknowledged.", "success")
    return redirect(url_for("dashboard.home"))
