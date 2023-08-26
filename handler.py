import os
import time
import uuid
from logger import logger
import json
import base64

from utils.utils import clean_folder, check_is_none
from utils.merge import merge_model
from io import BytesIO
import os
import runpod

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import *

for path in (LOGS_PATH, UPLOAD_FOLDER,CACHE_PATH):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error(f"Unable to create directory {path}: {str(e)}")

# regular cleaning
def clean_task():
    clean_folder(UPLOAD_FOLDER)
    clean_folder(CACHE_PATH)

scheduler = BackgroundScheduler()
scheduler.add_job(
    clean_task,
    trigger=IntervalTrigger(seconds=3600),
    id="clean_task"
)
scheduler.start()
# regular cleaning end

# load model
tts = merge_model(MODEL_LIST)

# Maximum number of jobs allowed in the queue
MAX_QUEUE_SIZE = int(os.environ.get("MAX_QUEUE_SIZE", 10))

# Create a job queue
job_queue = []


def concurrency_controller():
    # Check the number of jobs in the queue
    if len(job_queue) >= MAX_QUEUE_SIZE:
        return True  # Queue is full, concurrent execution not allowed
    else:
        return False  # Concurrent execution is allowed


async def handler(event):

    job_id = uuid.uuid4()
    job_queue.append(job_id)

    input = event['input']

    text = input['text']
    id = int(input['id'])
    format = "mp3"
    lang = "AUTO"
    length = float(input.get('length', 1.2))
    noise = float(input.get('noise', 0.667))
    noisew = float(input.get('noisew', 0.8))
    max = float(input.get('max', 50))

    logger.info(f"[VITS] id:{id} format:{format} lang:{lang} length:{length} noise:{noise} noisew:{noisew}")
    logger.info(f"[VITS] len:{len(text)} text：{text}")

    if check_is_none(text):
        logger.info(f"[VITS] text is empty")
        return json.dumps({"status": "error", "message": "text is empty"})

    if check_is_none(id):
        logger.info(f"[VITS] speaker id is empty")
        return json.dumps({"status": "error", "message": "speaker id is empty"})

    if id < 0 or id >= tts.vits_speakers_count:
        logger.info(f"[VITS] speaker id {id} does not exist")
        return json.dumps({"status": "error", "message": f"id {id} does not exist"})

    speaker_lang = tts.voice_speakers["VITS"][id].get('lang')
    if lang.upper() != "AUTO" and lang.upper() != "MIX" and len(speaker_lang) != 1 and lang not in speaker_lang:
        logger.info(f"[VITS] lang \"{lang}\" is not in {speaker_lang}")
        return make_response(jsonify({"status": "error", "message": f"lang '{lang}' is not in {speaker_lang}"}), 400)

    fname = f"{str(uuid.uuid1())}.{format}"
    task = {"text": text,
            "id": id,
            "format": format,
            "length": length,
            "noise": noise,
            "noisew": noisew,
            "max": max,
            "lang": lang,
            "speaker_lang": speaker_lang}

    t1 = time.time()
    audio = tts.vits_infer(task, fname)
    t2 = time.time()
    logger.info(f"[VITS] finish in {(t2 - t1):.2f}s")

    audio_base64 = base64.b64encode(audio.getvalue()).decode('utf-8')
    job_queue.remove(job_id)

    return audio_base64


if __name__ == '__main__':
    runpod.serverless.start(
        {
            'handler': handler,
            "concurrency_controller": concurrency_controller
        }
    )