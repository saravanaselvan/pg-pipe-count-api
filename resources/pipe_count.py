from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
import werkzeug
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
import cv2
from werkzeug.utils import secure_filename
import datetime
import os
from flask import current_app, send_file
import services.predict_detect.predict_det2 as predict_det2
from detectron2.config import get_cfg
from tasks.pipe_count_task import process_inference
from models.pipe import PipeModel
import json

ALLOWED_EXTENSIONS = {'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
class PipeCount(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True,
                        help="File is required")

    @jwt_required()
    def post(self):
        data = PipeCount.parser.parse_args()
        uploaded_file = data['file']
        original_file_name = secure_filename(uploaded_file.filename)
        uploaded_file_name = f'{original_file_name.split(".")[0]}_{datetime.datetime.now().strftime("%d_%m_%Y_%H:%M:%S")}.{original_file_name.rsplit(".", 1)[1]}'
        input_file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], uploaded_file_name)
        uploaded_file.save(input_file_path)            

        if allowed_file(uploaded_file.filename):
            try:
                pipe = PipeModel(
                    status="PENDING",
                    original_uploaded_file_name=original_file_name,
                    uploaded_file_name=uploaded_file_name,
                    output_file_name=original_file_name,
                )
                pipe.save_to_db()
            except BaseException as e:
                return f'{e}'
            process_inference.delay(
                pipe.id, current_app.config['OUTPUT_FOLDER'], current_app.config['UPLOAD_FOLDER'])
            # cfg = get_cfg()
            # np_image = predict_det2.input_fn(file, "application/octet-stream")
            # predictor = predict_det2.model_fn("services/predict_detect")
            # predictions = predict_det2.predict_fn(np_image, predictor)
            # predictions_json = predict_det2.output_fn(
            #     predictions, "application/json")

            return {"id": pipe.id}                

        else:
            return "Only png file type is accepted", 500

        # get image
        # img = Image.fromarray(np.uint8(v.get_image()[:, :, ::-1]))

        # Create the image with bounding boxes
        # print(predictions)
        # input_file_path = os.path.join(
        #     current_app.config['UPLOAD_FOLDER'], uploaded_file_name)

        # with open(input_file_path, 'wb') as fw:
        #     fw.write(file)
        #     fw.close()
        # v = Visualizer(
        #     cv2.imread(input_file_path)[:, :, :])
        # out = v.draw_instance_predictions(predictions["instances"].to(
        #     "cpu"))
        # cv2.imwrite(input_file_path, out.get_image()[:, :, ::-1])

class Uploads(Resource):

    @jwt_required()
    def get(self):
        pipes = PipeModel.query.filter_by(
            user_id=get_jwt_identity()).order_by(PipeModel.created_at.desc())
        return {
                    'pipes': [pipe.json() for pipe in pipes]
                }

class Pipe(Resource):

    @jwt_required()
    def get(self, id):
        pipe = PipeModel.query.filter_by(
            id=id, user_id=get_jwt_identity()).first()

        input_img_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], pipe.uploaded_file_name)

        return send_file(input_img_path, as_attachment=True)

class DownloadPredictions(Resource):

    @jwt_required()
    def get(self, id):
        pipe = PipeModel.query.filter_by(
            id=id, user_id=get_jwt_identity()).first()

        predictions_json = os.path.join(
            current_app.config['OUTPUT_FOLDER'], f"{pipe.id}/predictions.json")

        with open(predictions_json, 'r') as file:
            predictions_json_dict = json.loads(file.read())

        return {"predictions": predictions_json_dict}
