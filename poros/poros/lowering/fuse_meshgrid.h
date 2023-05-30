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
* @file fuse_meshgrid.h
* @author Lin Xiao Chun (linxiaochun@baidu.com)
* @date 2022-04-29 14:56:57
* @brief
**/

#pragma once

#include "poros/lowering/op_fuse_pass.h"

namespace baidu {
namespace mirana {
namespace poros {

class FuseMeshgrid : public IFuser {
public:
    FuseMeshgrid();

    bool fuse(std::shared_ptr<torch::jit::Graph> graph);

private:
    bool try_to_find_meshgrid(torch::jit::Block *block);

};

}
}
}