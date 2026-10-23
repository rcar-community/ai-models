# Copyright (C) 2026 Renesas Electronics Corporation
# Licensed under the Apache License, Version 2.0 (see LICENSES/Apache-2.0.txt).

# Export timm EfficientNet-Lite0 to ONNX for REACTION BYOM.
# Run with torch 2.4.1, the same version as in the REACTION .venv.

import os

import numpy as np
import onnxruntime
import timm
import torch

# ---- 1. Create the model -----------------------------------------------------
# timm model name and pretrained tag. The weights are published under Apache-2.0.
MODEL = "tf_efficientnet_lite0.in1k"
# Write the ONNX model next to this script
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tf_efficientnet_lite0.onnx")

model = timm.create_model(
    MODEL,
    pretrained=True,  # download the pretrained weights from Hugging Face (first run only)
    exportable=True,  # use layers that are easy to export to ONNX (static "SAME" padding)
).eval()  # inference mode (disables dropout etc.); required before export
# Input size and preprocessing (mean, std, crop_pct); preprocess.py follows these values
print(model.pretrained_cfg)

# ---- 2. Export to ONNX -------------------------------------------------------
# The shape of this input becomes the fixed input shape of the ONNX model:
# batch 1 (REACTION uses one fixed input_shape), RGB, 224x224 (pretrained_cfg input_size)
dummy = torch.rand(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy,
    OUT,
    input_names=["input"],  # REACTION default input name
    output_names=["output"],  # REACTION default output name
    opset_version=13,  # opset supported by REACTION (17 for transformer models)
    do_constant_folding=True,
)  # no dynamic_axes, to keep the shape fixed
print("saved", OUT)

# ---- 3. Check ----------------------------------------------------------------
with torch.no_grad():
    ref = model(dummy).numpy()
out = onnxruntime.InferenceSession(OUT).run(None, {"input": dummy.numpy()})[0]
# Expect (1, 1000) for the 1000 ImageNet classes, and a difference below about 1e-4
print("output shape:", out.shape, " max abs diff:", np.abs(ref - out).max())
