from flask import Flask
from flaskr.database import init_db
import flaskr.main.models


def create_app():
    app = Flask(__name__)
    # configを読み込む
    app.config.from_object('flaskr.config.Config')

    # DBを初期化
    init_db(app)

    # Blueprint
    from flaskr.main.views import main_bp
    from flaskr.api.v1.slack.api import api_v1_slack_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_v1_slack_bp)

    return app