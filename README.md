# Renesas AI Model Zoo for SparrowHawk

Pre-validated, INT8-quantized AI models and sample application code for the
Renesas R-Car V4H [SparrowHawk reference board](https://rcar-community.github.io/Sparrow-Hawk/).

> [!NOTE]
> First, install the [Renesas AI SDK](https://example.com/renesas-ai-sdk_DUMMY_LINK).
> The SDK includes **REACTION**, the Renesas edge AI compilation tool that quantizes,
> compiles, and deploys these models to the target.
> During installation, the SDK clones this repository into `<SDK workspace>/models/` so that the
> sample applications build and run on SparrowHawk out of the box.

## Included models

| Directory | Model | Upstream project |
|---|---|---|
| [`MobileNet_v1-app`](MobileNet_v1-app) | MobileNet v1 (1.0, 224) | [tensorflow/models](https://github.com/tensorflow/models/tree/archive/research/slim) (TF-Slim) |
| [`MobileNet_v2-app`](MobileNet_v2-app) | MobileNet v2 (1.0) | [onnx/models](https://github.com/onnx/models/tree/main/validated/vision/classification/mobilenet) (ONNX Model Zoo) |
| [`MultiNets-app`](MultiNets-app) | MobileNet v1 **and** v2, run concurrently | both of the above |
| [`ResNet18-app`](ResNet18-app) | ResNet18 | [open-mmlab/mmpretrain](https://github.com/open-mmlab/mmpretrain/tree/main/configs/resnet) |
| [`ResNet50-app`](ResNet50-app) | ResNet50 v1.5 | [mlcommons/inference](https://github.com/mlcommons/inference/tree/master/vision/classification_and_detection) (MLPerf reference) |

## Other contents

| Path | Description |
|---|---|
| [`app_models_requirements.csv`](app_models_requirements.csv) | Configuration file read by REACTION. Defines the model file and build options for each application. |
| [`LICENSES`](LICENSES) | Full text of the licenses referenced by this repository. |

## License

All files in this repository are licensed under
[Apache-2.0](LICENSES/Apache-2.0.txt) — both the Renesas-authored files
(Copyright Renesas Electronics Corporation) and the quantized ONNX models,
which derive from the upstream projects listed above, each published under
Apache-2.0.

There are no copyleft, non-commercial, or otherwise restricted files here. You
may redistribute any file in this repository, including inside a compiled
artifact such as the `.so` produced by the REACTION compilation flow, subject only to
the Apache-2.0 attribution and notice requirements.
