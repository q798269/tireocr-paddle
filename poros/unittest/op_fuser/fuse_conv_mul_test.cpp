// Copyright (c) 2022 Baidu, Inc.  All Rights Reserved.
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

/**
* @file: /icode-poros/baidu/mirana/poros/unnitest/op_fuser/fuse_conv_mul_test.cpp
* @author: zhangfan51@baidu.com
* @data: 2022-04-24 19:00:03
* @brief: 
**/ 

#include <gflags/gflags.h>
#include <gtest/gtest.h>

#include "poros/lowering/fuse_conv_mul.h"
#include "poros/lowering/op_fuse_pass.h"
#include "poros/util/graph_test_helper.h"

static std::vector<int64_t> ones(size_t n) {
    return std::vector<int64_t>(n, 1);
}

static std::vector<int64_t> zeros(size_t n) {
    return std::vector<int64_t>(n, 0);
}

static void fuse_test_helper(const std::string &graph_IR,
                             const size_t &dim,
                             std::shared_ptr<baidu::mirana::poros::IFuser> fuser,
                             std::vector<int64_t> input_shape,
                             std::vector<int64_t> conv_w_shape,
                             std::vector<int64_t> conv_b_shape
) {
    std::vector<at::IValue> input_data;
    input_data.push_back(at::randn(input_shape, {at::kCPU}));
    input_data.push_back(at::randn(conv_w_shape, {at::kCPU}));
    input_data.push_back(at::randn(conv_b_shape, {at::kCPU}));

    input_data.push_back(at::IntArrayRef(ones(dim))); //stride
    input_data.push_back(at::IntArrayRef(zeros(dim))); //padding
    input_data.push_back(at::IntArrayRef(ones(dim))); //dilation

    const std::vector<baidu::mirana::poros::graphtester::InputTypeEnum> input_data_type_mask = {
            baidu::mirana::poros::graphtester::InputTensor,

            baidu::mirana::poros::graphtester::ConstantTensor,
            baidu::mirana::poros::graphtester::ConstantTensor,

            baidu::mirana::poros::graphtester::ConstantIntVector,
            baidu::mirana::poros::graphtester::ConstantIntVector,
            baidu::mirana::poros::graphtester::ConstantIntVector,
    };

    baidu::mirana::poros::PorosOptions poros_option; // default device GPU
    // 运行原图与engine获取结果
    std::vector<at::Tensor> graph_output;
    std::vector<at::Tensor> fused_output;
    ASSERT_TRUE(baidu::mirana::poros::graphtester::run_graph_and_fused_graph(graph_IR, poros_option, fuser,
                                                                          input_data, input_data_type_mask,
                                                                          graph_output, fused_output));

    ASSERT_EQ(1, graph_output.size());
    ASSERT_EQ(1, fused_output.size());
    ASSERT_TRUE(baidu::mirana::poros::graphtester::almost_equal(graph_output[0], fused_output[0], 1e-6));
}

static std::string gen_conv3d_mul_graph() {
    return R"IR(
        graph(%x : Tensor, %conv_w : Tensor, %conv_b : Tensor, %conv_stride : Tensor, 
            %conv_padding : Tensor, %conv_dilation : Tensor):
          %3 : int = prim::Constant[value=1]()
          %4 : float = prim::Constant[value=2.0]()
          %conv_out : Tensor = aten::conv3d(%x, %conv_w, %conv_b, %conv_stride, %conv_padding, %conv_dilation, %3)
          %5 : Tensor = aten::mul(%conv_out, %4)
          return (%5))IR";
}

static std::string gen_conv2d_mul_graph() {

    return R"IR(
        graph(%x : Tensor, %conv_w : Tensor, %conv_b : Tensor, %conv_stride : Tensor, 
            %conv_padding : Tensor, %conv_dilation : Tensor):
          %3 : int = prim::Constant[value=1]()
          %4 : float = prim::Constant[value=2.0]()
          %conv_out : Tensor = aten::conv2d(%x, %conv_w, %conv_b, %conv_stride, %conv_padding, %conv_dilation, %3)
          %5 : Tensor = aten::mul(%conv_out, %4)
          return (%5))IR";
}

static std::string gen_conv1d_mul_graph() {

    return R"IR(
        graph(%x : Tensor, %conv_w : Tensor, %conv_b : Tensor, %conv_stride : Tensor, 
            %conv_padding : Tensor, %conv_dilation : Tensor):
          %3 : int = prim::Constant[value=1]()
          %4 : float = prim::Constant[value=2.0]()
          %conv_out : Tensor = aten::conv1d(%x, %conv_w, %conv_b, %conv_stride, %conv_padding, %conv_dilation, %3)
          %5 : Tensor = aten::mul(%conv_out, %4)
          return (%5))IR";
}

TEST(Fusers, ATenFuseConv3dMul_Test) {
    const auto graph_IR = gen_conv3d_mul_graph();
    auto fuser = std::make_shared<baidu::mirana::poros::FuseConvMul>();

    fuse_test_helper(graph_IR, 3, fuser, {1, 2, 3, 4, 5}, {3, 2, 3, 3, 3}, {3});
    fuse_test_helper(graph_IR, 3, fuser, {3, 5, 8, 4, 6}, {12, 5, 3, 3, 3}, {12});
    fuse_test_helper(graph_IR, 3, fuser, {1, 2, 3, 4, 5}, {3, 2, 3, 3, 3}, {3});
}

TEST(Fusers, ATenFuseConv2dMul_Test) {
    const auto graph_IR = gen_conv2d_mul_graph();
    auto fuser = std::make_shared<baidu::mirana::poros::FuseConvMul>();

    fuse_test_helper(graph_IR, 2, fuser, {1, 2, 4, 5}, {3, 2, 3, 3}, {3});
    fuse_test_helper(graph_IR, 2, fuser, {3, 5, 4, 6}, {12, 5, 3, 3}, {12});
    fuse_test_helper(graph_IR, 2, fuser, {1, 2, 4, 5}, {3, 2, 3, 3}, {3});
}

TEST(Fusers, ATenFuseConv1dMul_Test) {
    const auto graph_IR = gen_conv1d_mul_graph();
    auto fuser = std::make_shared<baidu::mirana::poros::FuseConvMul>();

    fuse_test_helper(graph_IR, 1, fuser, {1, 2, 5}, {3, 2, 3}, {3});
    fuse_test_helper(graph_IR, 1, fuser, {3, 5, 6}, {12, 5, 3}, {12});
    fuse_test_helper(graph_IR, 1, fuser, {1, 2, 5}, {3, 2, 3}, {3});
}