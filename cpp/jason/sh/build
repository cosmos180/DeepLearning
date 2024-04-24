#!/bin/bash

###
 # @Author: bughero jinxinhou@tuputech.com
 # @Date: 2023-09-13 11:15:14
 # @LastEditors: bughero jinxinhou@tuputech.com
 # @LastEditTime: 2023-09-13 11:46:11
 # @FilePath: /DeepLearning/cpp/jason/sh/build.sh
 # @Description: 
 # 
 # Copyright (c) 2023 by 图普科技, All Rights Reserved. 
### 
CURRENT_DIR="$(pwd)"
# echo ${CURRENT_DIR}

BUILD_DIR=${CURRENT_DIR}/build
mkdir -p ${BUILD_DIR}

pushd ${BUILD_DIR}


CMAKE_FILE_PATH="../"

CMAKE_ARGS="${CMAKE_ARGS}"
cmake ${CMAKE_ARGS} ${CMAKE_FILE_PATH}
cmake --build . --parallel

popd


