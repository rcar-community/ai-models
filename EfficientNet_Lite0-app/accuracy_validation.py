# Copyright (C) 2026 Renesas Electronics Corporation
# Licensed under the Apache License, Version 2.0 (see LICENSES/Apache-2.0.txt).

# Compute the Top-1 / Top-5 accuracy of timm EfficientNet-Lite0 on ImageNet images.
# Set this script as "command" in reaction.yaml and run "reaction start" (runs in Docker).
# -ra selects the inference method (same argument as the REACTION BYOM sample):
#   no -ra  : run the FP32 ONNX model with onnxruntime
#   -ra qdq : run the ONNX model quantized by REACTION with onnxruntime
#   -ra tvm : run the model compiled by REACTION with TVM on the board

import argparse
import os
import sys

import numpy as np
import onnxruntime
from tqdm import tqdm

# Use preprocess.py next to this script, so that quantization and evaluation match
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocess import preprocess_image, read_image_list


def parse_args():
    p = argparse.ArgumentParser(description="Compute the Top-1 / Top-5 accuracy of EfficientNet-Lite0")
    p.add_argument("-onnx", "--onnx_path", required=True,
                   help="FP32 ONNX model (also given with -ra qdq / tvm, as the source of quantization)")
    p.add_argument("-ra", "--reaction", choices=["qdq", "tvm"], default=None,
                   help="inference method; FP32 if omitted")
    p.add_argument("-ss", "--subset", type=int, default=1000,
                   help="number of images to evaluate (from the top of the list)")
    return p.parse_args()


def build_predictor(args):
    """Return a function that takes an input and returns the model output, for -ra."""
    if args.reaction is None:  # FP32: run the exported ONNX model as is
        print("FP32: running on the host with onnxruntime:", args.onnx_path)
        sess = onnxruntime.InferenceSession(args.onnx_path)
        name = sess.get_inputs()[0].name
        return lambda x: sess.run(None, {name: x})[0]

    from reaction.get import initialize_reaction  # read reaction.yaml
    deploy_cfg, model_cfg = initialize_reaction()

    if args.reaction == "qdq":  # INT8 on the host: find the ONNX model quantized by REACTION
        from reaction.manager import FetchArtifacts
        quant_onnx = FetchArtifacts(deploy_cfg, model_cfg).quant_onnx[0]
        print("INT8 (QDQ): running on the host with onnxruntime:", quant_onnx)
        sess = onnxruntime.InferenceSession(quant_onnx)
        name = sess.get_inputs()[0].name
        return lambda x: sess.run(None, {name: x})[0]

    # INT8 on the board: run the model compiled with TVM
    from reaction.convert.tvm.evaluate_tvm import BackendTVM
    backend = BackendTVM()
    model = backend.load(deploy_cfg)  # connect to the board given by host / port in reaction.yaml
    print("INT8 (TVM): running on the board")
    input_name = deploy_cfg.onnx_config.input_names[0]
    return lambda x: model.predict({input_name: x})[0]


def main():
    args = parse_args()
    predict = build_predictor(args)
    items = read_image_list()[: args.subset]  # (image path, class index)

    top1 = top5 = 0
    for path, label in tqdm(items, desc="Evaluating", unit="img"):
        scores = np.asarray(predict(preprocess_image(path)))[0]  # 1000 class scores
        ranking = np.argsort(scores)[::-1]
        top1 += int(ranking[0] == label)
        top5 += int(label in ranking[:5])

    n = len(items)
    print(f"TOP1 Accuracy: {top1 / n * 100:.2f}%  ({top1}/{n})")
    print(f"TOP5 Accuracy: {top5 / n * 100:.2f}%  ({top5}/{n})")

    # Record the accuracy in REACTION (same as the BYOM sample): the FP32 reference
    # without -ra, or the INT8 value with -ra qdq, used by the optimal / sensitive search.
    # Uses EXP_NAME set by REACTION, so run it with "reaction start".
    from reaction.tools.utility.byom import BYOMhelper
    BYOMhelper().update_acc(top1 / n * 100, args.reaction)


if __name__ == "__main__":
    main()
