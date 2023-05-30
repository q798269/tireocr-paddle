// Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include <string>

#include "common.h"
#include "fastdeploy/vision.h"
#ifdef WIN32
const char sep = '\\';
#else
const char sep = '/';
#endif

void InitAndInfer(const std::string& model_dir, const std::string& image_file,
                  const std::string& cls_result) {
  auto model_file = model_dir + sep + "inference.pdmodel";
  auto params_file = model_dir + sep + "inference.pdiparams";
  auto config_file = model_dir + sep + "inference_cls.yaml";
  fastdeploy::vision::EnableFlyCV();
  fastdeploy::RuntimeOption option;
  option.UseTimVX();

  auto model = fastdeploy::vision::classification::PaddleClasModel(
      model_file, params_file, config_file, option);

  assert(model.Initialized());

  auto im = cv::imread(image_file);

  fastdeploy::vision::ClassifyResult res;
  if (!model.Predict(im, &res)) {
    std::cerr << "Failed to predict." << std::endl;
    return;
  }

  if (CompareClsResult(res, cls_result)) {
    std::cout << model_dir + " run successfully." << std::endl;
  } else {
    std::cerr << model_dir + " run failed." << std::endl;
  }
}

int main(int argc, char* argv[]) {
  if (argc < 4) {
    std::cout
        << "Usage: test_clas path/to/quant_model "
           "path/to/image "
           "e.g ./test_clas ./ResNet50_vd_quant ./test.jpeg resnet50_clas.txt"
        << std::endl;
    return -1;
  }

  std::string model_dir = argv[1];
  std::string test_image = argv[2];
  std::string cls_result = argv[3];
  InitAndInfer(model_dir, test_image, cls_result);
  return 0;
}
