from flask import Flask
from config import Config
from models import db
from routes.auth import auth
from routes.dashboard import dashboard
from models import LoginLog



app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(dashboard)

@app.route("/")
def home():
    return "AI Login Security System Running"

@app.route("/logs")
def view_logs():
    logs = LoginLog.query.all()
    output = ""

    for log in logs:
        output += (
            f"User: {log.user_id}, "
            f"Hour: {log.login_hour}, "
            f"Day: {log.day_of_week}, "
            f"IP Group: {log.ip_group}, "
            f"Device: {log.device_type}<br>"
        )

    return output



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

