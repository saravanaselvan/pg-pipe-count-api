from datetime import timedelta
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS

from db import db, migrate
from resources.auth import Login
from resources.user import UserRegister
from resources.pipe_count import PipeCount
from resources.pipe_count import Uploads
from resources.pipe_count import Pipe
from resources.pipe_count import DownloadPredictions

from dotenv import load_dotenv
from celery_util import make_celery
from base import celery

load_dotenv()

app = Flask(__name__)
CORS(app)
uri = os.environ.get(
    'DATABASE_URL', 'test.db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=4)
app.config.from_pyfile('config.py')

UPLOAD_FOLDER = os.environ.get(
    'UPLOAD_FOLDER', 'private/input_videos')
OUTPUT_FOLDER = os.environ.get(
    'OUTPUT_FOLDER', 'private/output_files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

upload_dir = os.path.join(UPLOAD_FOLDER)
os.makedirs(upload_dir, exist_ok=True)
output_dir = os.path.join(OUTPUT_FOLDER)
os.makedirs(output_dir, exist_ok=True)

api = Api(app)

jwt = JWTManager(app)
make_celery(app, celery)
api.add_resource(PipeCount, '/api/pipe_count')
api.add_resource(Uploads, '/api/uploads')
api.add_resource(Pipe, '/api/pipe/<int:id>')
api.add_resource(DownloadPredictions, '/api/download_predictions/<int:id>')
api.add_resource(UserRegister, '/api/register')
api.add_resource(Login, '/api/login')

db.init_app(app)
migrate.init_app(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":

    app.run(debug=True)
