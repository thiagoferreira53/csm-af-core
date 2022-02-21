import os

from config import get_allowable_origins
from app import create_app
from flask_cors import CORS

#I must set this environment variable inside the docker-compose.yml
os.environ['AFDB_URL'] = 'postgresql://postgres:weather@localhost:5432/weather_data'
os.environ['AFAPI_ALLOWABLE_ORIGINS'] = '*'


app = create_app(
    {
        "SQLALCHEMY_DATABASE_URI": os.getenv("AFDB_URL"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {"pool_pre_ping": True},
    }
)

allowable_origins = get_allowable_origins()
CORS(app, resources={r"/v1/*": {"origins": allowable_origins}})

#if __name__ == "__main__":
#     app.run(debug=os.getenv("DEBUG", False), host="0.0.0.0")
