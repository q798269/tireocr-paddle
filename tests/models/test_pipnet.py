# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fastdeploy as fd
import cv2
import os
import numpy as np


def test_facealignment_pipnet():
    model_url = "https://bj.bcebos.com/paddlehub/fastdeploy/pipnet_resnet18_10x19x32x256_aflw.onnx"
    input_url = "https://bj.bcebos.com/paddlehub/fastdeploy/facealign_input.png"
    output_url = "https://bj.bcebos.com/paddlehub/fastdeploy/tests/pipnet_result_landmarks.npy"
    fd.download(model_url, ".")
    fd.download(input_url, ".")
    fd.download(output_url, ".")
    model_path = "pipnet_resnet18_10x19x32x256_aflw.onnx"
    # use ORT
    runtime_option = fd.RuntimeOption()
    runtime_option.use_ort_backend()
    model = fd.vision.facealign.PIPNet(
        model_path, runtime_option=runtime_option)

    # compare diff
    im = cv2.imread("./facealign_input.png")
    result = model.predict(im.copy())
    expect = np.load("./pipnet_result_landmarks.npy")

    diff = np.fabs(np.array(result.landmarks) - expect)
    thres = 1e-04
    assert diff.max() < thres, "The diff is %f, which is bigger than %f" % (
        diff.max(), thres)
