import multiprocessing
import os

bind = "0.0.0.0:23456"
workers = int(os.environ.get('WORKERS', 1))
workers = min(workers, multiprocessing.cpu_count())


# MODEL_LIST = [[ABS_PATH + "/models/vctk/pretrained_vctk.pth", ABS_PATH + "/models/vctk/config.json"]]
# git lfs install
# git clone https://huggingface.co/abhishekgoyal/vctk-vits models/vctk