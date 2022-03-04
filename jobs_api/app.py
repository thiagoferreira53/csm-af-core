import datetime

from database import db
from flask.app import Flask
from flask.json import JSONEncoder


# encoder
class CustomJSONEncoder(JSONEncoder):  # pragma: no cover
    "Add support for serializing timedeltas"

    def default(self, o):
        if type(o) == datetime.timedelta:
            return str(o)
        elif type(o) == datetime.datetime:
            return o.isoformat()
        else:
            return super().default(o)


def create_app(settings: dict = None):
    app = Flask(__name__)
    if settings:
        app.config.update(settings)
    app.json_encoder = CustomJSONEncoder

    from af_endpoints import af_apis

    app.register_blueprint(af_apis)

    from af_request.views import af_requests_bp

    app.register_blueprint(af_requests_bp)

    db.init_app(app)
    return app
