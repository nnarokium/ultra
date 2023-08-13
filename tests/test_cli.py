# Ultralytics YOLO 🚀, AGPL-3.0 license

import subprocess
from pathlib import Path

import pytest

from ultralytics.utils import ONLINE, ROOT, SETTINGS

WEIGHT_DIR = Path(SETTINGS['weights_dir'])
TASK_ARGS = [
    ('detect', 'yolov8n', 'coco8.yaml'),
    ('segment', 'yolov8n-seg', 'coco8-seg.yaml'),
    ('classify', 'yolov8n-cls', 'imagenet10'),
    ('pose', 'yolov8n-pose', 'coco8-pose.yaml'), ]  # (task, model, data)
EXPORT_ARGS = [
    ('yolov8n', 'torchscript'),
    ('yolov8n-seg', 'torchscript'),
    ('yolov8n-cls', 'torchscript'),
    ('yolov8n-pose', 'torchscript'), ]  # (model, format)


def run(cmd):
    # Run a subprocess command with check=True
    subprocess.run(cmd.split(), check=True)


def test_special_modes():
    run('yolo checks')
    run('yolo settings')
    run('yolo help')


@pytest.mark.parametrize('task,model,data', TASK_ARGS)
def test_train(task, model, data):
    run(f'yolo train {task} model={model}.yaml data={data} imgsz=32 epochs=1 cache=disk')


@pytest.mark.parametrize('task,model,data', TASK_ARGS)
def test_val(task, model, data):
    run(f'yolo val {task} model={model}.pt data={data} imgsz=32')


@pytest.mark.parametrize('task,model,data', TASK_ARGS)
def test_predict(task, model, data):
    run(f"yolo predict model={model}.pt source={ROOT / 'assets'} imgsz=32 save save_crop save_txt")


@pytest.mark.skipif(not ONLINE, reason='environment is offline')
@pytest.mark.parametrize('task,model,data', TASK_ARGS)
def test_predict_online(task, model, data):
    mode = 'track' if task in ('detect', 'segment', 'pose') else 'predict'  # mode for video inference
    run(f'yolo predict model={model}.pt source=https://ultralytics.com/images/bus.jpg imgsz=32')
    run(f'yolo {mode} model={model}.pt source=https://ultralytics.com/assets/decelera_landscape_min.mov imgsz=32')


@pytest.mark.parametrize('model,format', EXPORT_ARGS)
def test_export(model, format):
    run(f'yolo export model={model}.pt format={format} imgsz=32')


# Test SAM, RTDETR Models
def test_rtdetr(task='detect', model='yolov8n-rtdetr.yaml', data='coco8.yaml'):
    # Warning: MUST use imgsz=640
    run(f'yolo detect train {task} model={model} data={data} imgsz=640 epochs=1 cache=disk')
    run(f'yolo detect val {task} model={model} data={data} imgsz=640')
    run(f"yolo detect predict model={model} source={ROOT / 'assets/bus.jpg'} imgsz=640 save save_crop save_txt")


def test_fastsam(task='segment', model='FastSAM-s.pt', data='coco8-seg.yaml'):
    # run(f'yolo segment val {task} model={model} data={data} imgsz=640')  # TODO: FIX ERROR HERE
    run(f"yolo segment predict model={model} source={ROOT / 'assets/bus.jpg'} imgsz=32 save save_crop save_txt")


def test_mobilesam():
    from ultralytics import SAM

    # Load the model
    model = SAM('mobile_sam.pt')

    # Predict a segment based on a point prompt
    model.predict(ROOT / 'assets/zidane.jpg', points=[900, 370], labels=[1])

    # Predict a segment based on a box prompt
    model.predict(ROOT / 'assets/zidane.jpg', bboxes=[439, 437, 524, 709])


# Slow Tests
@pytest.mark.slow
@pytest.mark.parametrize('task,model,data', TASK_ARGS)
def test_train_gpu(task, model, data):
    run(f'yolo train {task} model={model}.yaml data={data} imgsz=32 epochs=1 device="0"')  # single GPU
    run(f'yolo train {task} model={model}.pt data={data} imgsz=32 epochs=1 device="0,1"')  # Multi GPU
