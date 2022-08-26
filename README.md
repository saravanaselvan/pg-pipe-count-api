# pg-pipe-count-api

Install the below libraries before running the Flask App:

RabbitMQ - https://www.rabbitmq.com/download.html

# Project Setup:

git clone https://github.com/saravanaselvan/pg-pipe-count-api.git

cd pg-pipe-count-api

mkdir private

mkdir private/uploads

mkdir private/output_files

Copy **model_final.pth** file to **services/predict_detect** folder. This is the trained pyTorch model to detect pipes from the uploaded picture.

touch private/celery.log

# Configuration files:

Create .env and config.py in the project root directory as below - 

# .env

export DATABASE_URL="mysql+pymysql://[USERNAME]:[PASSWORD]@[HOST]/[DATABASE]"

export UPLOAD_FOLDER = 'private/uploads'

export OUTPUT_FOLDER = 'private/output_files'

export MODEL_NAME = '0'


# config.py

JWT_SECRET_KEY = '[RANDOM KEY]'

SQLALCHEMY_TRACK_MODIFICATIONS = False

PROPAGATE_EXCEPTIONS = True

JSON_SORT_KEYS = False

BROKER_URL = "amqp://localhost/"

CELERY_RESULT_BACKEND = "db+mysql+pymysql://[USERNAME]:[PASSWORD]@[HOST]/[DATABASE]"


# PIP Install Requirements:

python3 -m venv pg-venv

. pg-venv/bin/activate

python3 -m pip install -r requirements.txt

# Install pyTorch & Detectron2:

python3 -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

* Install Detectron2 with this commit due to an issue in latest commit. Please refer - https://stackoverflow.com/a/73413073/1341118

python3 -m pip pip install 'git+https://github.com/facebookresearch/detectron2.git@5aeb252b194b93dc2879b4ac34bc51a31b5aee13'

# Background Task:

sudo rabbitmq-server

celery -A app.celery  worker -f ~/private/celery.log --loglevel=info

# Run the app in port 8000:
python3 app.py
