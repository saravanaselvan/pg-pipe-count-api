import os
import cv2
from base import celery as celery_app
import services.predict_detect.predict_det2 as predict_det2
from detectron2.config import get_cfg
from models.pipe import PipeModel


@celery_app.task(name="pg_pipe_count.process_inference")
def process_inference(id, output_folder, upload_folder):
    pipe = PipeModel.query.filter_by(id=id).first()
    pipe.status = "IN PROGRESS"
    pipe.save_to_db()
    output_dir = f"{output_folder}/{pipe.id}"
    os.makedirs(output_dir, exist_ok=True)

    input_file_path = os.path.join(
        upload_folder, pipe.uploaded_file_name)

    with open(input_file_path, 'rb') as f:
        file = f.read()

    # file = cv2.imread(input_file_path)

    cfg = get_cfg()
    np_image = predict_det2.input_fn(file, "application/octet-stream")

    print("INPUT IMAGE", np_image)
    predictor = predict_det2.model_fn("services/predict_detect")
    predictions = predict_det2.predict_fn(np_image, predictor)
    predictions_json = predict_det2.output_fn(
        predictions, "application/json")

    prediction_json_path = f"{output_dir}/predictions.json"
    with open(prediction_json_path, 'w') as file:
        file.write(predictions_json)
        file.close()

    pipe.output_file_name = pipe.original_uploaded_file_name
    pipe.output_file_path = f"{output_folder}/{pipe.id}/{pipe.original_uploaded_file_name}"
    pipe.status = "COMPLETED"

    pipe.save_to_db()
