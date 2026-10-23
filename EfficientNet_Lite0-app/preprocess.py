# Copyright (C) 2026 Renesas Electronics Corporation
# Licensed under the Apache License, Version 2.0 (see LICENSES/Apache-2.0.txt).

# Preprocessing of timm EfficientNet-Lite0 and the calibration data reader for quantization.
# When this file is registered as the preprocess script, REACTION uses QuantDataReader
# for calibration (without it, calibration uses random data and accuracy drops a lot).
# accuracy_validation.py also uses preprocess_image, so that quantization and
# evaluation use the same preprocessing.

import os

import numpy as np
from PIL import Image
from onnxruntime.quantization import CalibrationDataReader

# ---- Preprocessing parameters (pretrained_cfg printed by onnx_export.py) -----
RESIZE = 256  # resize the short side to this length (224 / crop_pct 0.875)
CROP = 224  # center crop size (model input size)
MEAN = (0.5, 0.5, 0.5)  # pretrained_cfg mean (not the usual ImageNet mean)
STD = (0.5, 0.5, 0.5)  # pretrained_cfg std (not the usual ImageNet std)

# ---- Dataset location ----------------------------------------------------------
DOCKER_DATA_DIR = "/workspace/data"  # REACTION mounts DATA_DIR here in its containers
if os.path.isdir(DOCKER_DATA_DIR):
    DATA_DIR = DOCKER_DATA_DIR
else:  # running directly on the host
    DATA_DIR = os.environ.get("DATA_DIR", os.path.expanduser("~/ai_sdk_datasets"))
# ImageNet validation images; not stored under models/ because of the dataset license
IMAGENET_DIR = os.path.join(DATA_DIR, "imagenet")


def preprocess_image(path):
    """Convert one image file to the model input: float32 of shape (1, 3, 224, 224)."""
    img = Image.open(path).convert("RGB")  # ImageNet contains grayscale and CMYK images

    # Resize the short side to RESIZE, keeping the aspect ratio (as torchvision Resize)
    w, h = img.size
    if w < h:
        nw, nh = RESIZE, int(RESIZE * h / w)
    else:
        nw, nh = int(RESIZE * w / h), RESIZE
    img = img.resize((nw, nh), Image.BICUBIC)  # pretrained_cfg interpolation

    # Center crop (as torchvision CenterCrop)
    left = int(round((nw - CROP) / 2.0))
    top = int(round((nh - CROP) / 2.0))
    img = img.crop((left, top, left + CROP, top + CROP))

    x = np.asarray(img, dtype=np.float32) / 255.0  # 0-255 to 0-1
    x = (x - MEAN) / STD  # normalize per channel
    x = x.transpose(2, 0, 1)  # HWC to CHW, as the ONNX input is NCHW
    return x[np.newaxis].astype(np.float32)  # add the batch dimension


def read_image_list(imagenet_dir=IMAGENET_DIR):
    """Read (image path, class index) pairs from meta/val.txt."""
    items = []
    with open(os.path.join(imagenet_dir, "meta", "val.txt")) as f:
        for line in f:  # each line: "<path relative to val/> <class index>"
            parts = line.split()
            if len(parts) >= 2:
                items.append((os.path.join(imagenet_dir, "val", parts[0]), int(parts[1])))
    return items


class QuantDataReader(CalibrationDataReader):  # class name required by REACTION
    """Feed calibration images one by one during quantization."""

    def __init__(self, deploy_cfg, model_cfg):  # REACTION calls it with these arguments
        super().__init__()
        self.input_name = deploy_cfg.onnx_config.input_names[0]  # 'input'
        # Number of calibration images from the REACTION config (default 100)
        count = deploy_cfg.backend_config.quantization_config.dataset_samples
        items = read_image_list()
        # Pick images at equal intervals: val.txt is sorted by class, so taking the
        # first images would cover only a few classes
        step = max(1, len(items) // count)
        paths = [p for p, _ in items[::step][:count]]
        self.data = [{self.input_name: preprocess_image(p)} for p in paths]  # about 60 MB for 100
        self.rewind()

    def get_next(self):  # next calibration input, or None at the end
        if self.pos >= len(self.data):
            return None
        item = self.data[self.pos]
        self.pos += 1
        return item

    def rewind(self):  # go back to the first input
        self.pos = 0

    def __len__(self):  # number of calibration inputs
        return len(self.data)

    def __getitem__(self, indices):  # a reader for a range, used for split calibration
        assert isinstance(indices, slice)
        sub = QuantDataReader.__new__(QuantDataReader)  # reuse the preprocessed data
        sub.input_name = self.input_name
        sub.data = self.data[indices]
        sub.rewind()
        return sub
