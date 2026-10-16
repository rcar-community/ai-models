// Copyright (C) 2026 Renesas Electronics Corporation
// Licensed under the Apache License, Version 2.0 (see LICENSES/Apache-2.0.txt).

#include "prepostproc.h"

#include <cstdint>
#include <fstream>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <ostream>
#include <string>

static void copy_image_to_input_buffer_and_quantize(void* input, const cv::Mat& normalized_image,
                                                    int width, int height, int channels,
                                                    const quantization_parameters& qp) {
  std::cout << "Setting input" << std::endl;
  float* image_data = reinterpret_cast<float*>(normalized_image.data);
  int8_t* input_data = reinterpret_cast<int8_t*>(input);
  for (int i = 0; i < height; ++i) {
    for (int j = 0; j < width; ++j) {
      for (int k = 0; k < channels; ++k) {
        float res =
            (image_data[i * width * channels + j * channels + k] / qp.scale_factor) + qp.zero_point;
        input_data[k * width * height + i * width + j] = res;
      }
    }
  }
}

static void _preprocess_input(cv::Mat& normalized_image, const cv::Mat& image, int width,
                              int height) {
  cv::cvtColor(image, image, cv::COLOR_BGR2RGB);

  cv::Mat resized_image;
  double factor = 256.0 / (image.cols < image.rows ? image.cols : image.rows);
  cv::resize(image, resized_image, cv::Size(image.cols * factor, image.rows * factor));

  int x = (resized_image.cols - width) / 2;
  int y = (resized_image.rows - height) / 2;
  cv::Mat cropped_image = resized_image(cv::Rect(x, y, width, height));

  cropped_image.convertTo(normalized_image, CV_32F, 1.0 / 255.0);
  cv::Scalar mean(0.485, 0.456, 0.406);
  cv::Scalar std(0.229, 0.224, 0.225);
  cv::subtract(normalized_image, mean, normalized_image);
  cv::divide(normalized_image, std, normalized_image);
}

void preprocess_input(const char* model_name, const int input_idx, void* input, tvm::runtime::ShapeTuple shape,
                      IndependentType dtype, const char* path_to_input_file,
                      const quantization_parameters& qp) {
  std::cout << "Loading image " << path_to_input_file;
  std::string shape_str = "";
  int channels = shape[1];
  int height = shape[2];
  int width = shape[3];
  for (int shape_idx = 0; shape_idx < shape.size(); shape_idx++) {
    shape_str += std::to_string(shape[shape_idx]) + "x";
  }
  std::cout << "(" << shape_str << "): " << dtype << std::endl;

  const cv::Mat image = cv::imread(path_to_input_file);
  cv::Mat normalized_image;
  _preprocess_input(normalized_image, image, width, height);
  copy_image_to_input_buffer_and_quantize(input, normalized_image, width, height, channels, qp);
}

static void callback_postprocess(const int id, void* output, tvm::runtime::ShapeTuple shape,
                                 const quantization_parameters& qp) {
  int32_t top1_idx = -1;
  float top1_score = -128;
  int32_t output_size = 1;
  {
    int8_t* output_data = static_cast<int8_t*>(output);
    for (int shape_idx = 0; shape_idx < shape.size(); shape_idx++) {
      output_size *= shape[shape_idx];
    }
    for (int i = 0; i < output_size; ++i) {
      float dequantized_value = (((int32_t)output_data[i]) - qp.zero_point) * qp.scale_factor;
      if (dequantized_value > top1_score) {
        top1_idx = i;
        top1_score = dequantized_value;
      }
    }
  }
  std::cout << "Thread (" << id << ") Top-1 prediction: " << top1_idx << " " << +top1_score
            << std::endl;
}

void postprocess_output(const char* model_name, std::vector<OutputInfo>& output_info) {
  OutputInfo& oi = output_info[0];
  if (oi.global_idx >= 0 && oi.global_idx <= 3) {
    callback_postprocess(oi.global_idx, oi.ptr, oi.shape, oi.qp);
  } else {
    std::cerr << "Unexpected output_idx " << +oi.global_idx << ". Exiting" << std::endl;
    exit(1);
  }
}
