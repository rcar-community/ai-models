# EfficientNet_Lite0-app: BYOM example artifacts

Ready-made outputs of every step of the REACTION BYOM (Bring Your Own Model)
tutorial for EfficientNet-Lite0: from exporting the model to ONNX, through
quantization and accuracy evaluation, to running it as a common application on
SparrowHawk. Use them to check your own results, or to skip any step of the
tutorial and start from the next one.

> [!NOTE]
> For the procedure, see the [BYOM tutorial](https://example.com/renesas-ai-sdk-byom_DUMMY_LINK).
> Once registered, the common application runs in the same way as
> [`MobileNet_v1-app`](../MobileNet_v1-app).

## Model

| | |
|---|---|
| Model | EfficientNet-Lite0, ImageNet-1k classification, input 1x3x224x224 |
| Upstream | [huggingface/pytorch-image-models](https://github.com/huggingface/pytorch-image-models) (timm), weights `tf_efficientnet_lite0.in1k` |
| License | Apache-2.0 (code and weights) |

EfficientNet-Lite is designed for quantized inference: it uses ReLU6 only and
has no Squeeze-and-Excitation blocks. INT8 quantization costs only 0.2 points
of Top-1 accuracy (see the expected results below).

> [!IMPORTANT]
> This model is normalized with mean (0.5, 0.5, 0.5) and std (0.5, 0.5, 0.5),
> not with the usual ImageNet values. `preprocess.py`, `prepostproc.cc` and the
> input `quantize` values in `exec_config.json` follow this.

## Files

| File | Produced in | Use it to skip |
|---|---|---|
| `onnx_export.py` | Export to ONNX | — (script that exports the FP32 ONNX model) |
| `tf_efficientnet_lite0.onnx` | Export to ONNX | setting up PyTorch / timm and exporting the model |
| `preprocess.py` | Preparing the scripts | writing the preprocessing and the calibration data reader |
| `accuracy_validation.py` | Preparing the scripts | writing the accuracy evaluation script |
| `byom_requirements.csv`, `byom.Dockerfile` | BYOM registration (`reaction bond --with-docker`) | the registration (see below) |
| `tf_efficientnet_lite0_sim_quant.onnx` | Quantization (`reaction start`) | quantization |
| `CMakeLists.txt`, `modified_config.json` | Common application | — (same as `MobileNet_v1-app`) |
| `exec_config.json`, `prepostproc.cc` | Common application | adapting the `MobileNet_v1-app` files to this model |
| `user_app_models_requirements.csv` | Common application registration | adding the application row (see below) |

All commands below are run in the REACTION directory of the SDK workspace,
which contains this repository as `models/`.

### Skip the BYOM registration

Register the model and build the accuracy evaluation image without running
`reaction bond --with-docker`:

```bash
mkdir -p register/configs/byom inference/byom/EfficientNet_Lite0
cp models/EfficientNet_Lite0-app/byom_requirements.csv register/configs/byom/byom_requirements.csv
cp models/EfficientNet_Lite0-app/byom.Dockerfile inference/byom/EfficientNet_Lite0/
docker build -t reaction/byom-v4h2-cpu:v3.47.0 -f inference/byom/EfficientNet_Lite0/byom.Dockerfile .
```

- `register/configs/byom/byom_requirements.csv` holds all BYOM models. If you
  have already registered other models, add only the second line of the file.
- Create `inference/` yourself as above: if it does not exist, Docker creates
  it owned by root, and a later `reaction bond` fails.
- `v3.47.0` in the CSV (`engine`) and in `byom.Dockerfile` is the SDK version.

### Register the common application

Add the second line of `user_app_models_requirements.csv` to
`register/application/user/user_app_models_requirements.csv`, then set
`model_name: EfficientNet_Lite0-app` and `action: app` in `reaction.yaml`.

## Expected results

Accuracy on 1000 ImageNet validation images, with the default quantization
settings (INT8, MinMax, 100 calibration images):

| Evaluation | Top-1 | Top-5 |
|---|---|---|
| FP32, onnxruntime | 73.90% | 90.40% |
| INT8 (QDQ), onnxruntime | 73.70% | 90.40% |
| INT8, TVM on SparrowHawk (RPC) | 73.60% | 90.40% |

Common application on SparrowHawk (4 threads):

| Input | Top-1 class |
|---|---|
| `cat.jpg` | 282 (tiger cat) |
| `duck.jpg` | 97 (drake) |
| `golden_retriever.jpg` | 207 (golden retriever) |
| `malard.jpg` | 97 (drake) |

The throughput is about 77 fps in total over the 4 threads (about 19 fps per
thread), measured with `number_of_loops` 100 and `print_inference` false. The
CNN-IP part of the compiled model is a single piece, so little data is passed
between the CNN-IP and the CPU.

The ImageNet images are not included in this repository because of the dataset
license. Place them under `DATA_DIR` as described in the tutorial.
