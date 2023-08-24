import multiprocessing
import os

bind = "0.0.0.0:23456"
worker_class = 'gevent'
workers = int(os.environ.get('WORKERS', 1))
workers = min(workers, multiprocessing.cpu_count())
threads = int(os.environ.get('THREADS', 8))
timeout = 30

# MODEL_LIST = [[ABS_PATH + "/models/vctk/pretrained_vctk.pth", ABS_PATH + "/models/vctk/config.json"]]
# git lfs install
# git clone https://huggingface.co/abhishekgoyal/vctk-vits models/vctk

##CPU
# docker build -t vits-cpu -f Dockerfile2 .
# docker tag vits-cpu gemsford/vits:cpu
# docker push gemsford/vits:cpu