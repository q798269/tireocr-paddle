PROJECT(infer_demo C CXX)
CMAKE_MINIMUM_REQUIRED (VERSION 3.10)

# 指定下载解压后的fastdeploy库路径
option(FASTDEPLOY_INSTALL_DIR "Path of downloaded fastdeploy sdk.")

include(${FASTDEPLOY_INSTALL_DIR}/FastDeploy.cmake)

# 添加FastDeploy依赖头文件
include_directories(${FASTDEPLOY_INCS})
include_directories(${FastDeploy_INCLUDE_DIRS})

add_executable(ppyoloe_infer_demo ${PROJECT_SOURCE_DIR}/infer_ppyoloe.cc)
add_executable(picodet_infer_demo ${PROJECT_SOURCE_DIR}/infer_picodet.cc)
# 添加FastDeploy库依赖
target_link_libraries(ppyoloe_infer_demo ${FASTDEPLOY_LIBS})
target_link_libraries(picodet_infer_demo ${FASTDEPLOY_LIBS})

set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/build/install)

install(TARGETS ppyoloe_infer_demo DESTINATION ./)
install(TARGETS picodet_infer_demo DESTINATION ./)

install(DIRECTORY models DESTINATION ./)
install(DIRECTORY images DESTINATION ./)

file(GLOB_RECURSE FASTDEPLOY_LIBS ${FASTDEPLOY_INSTALL_DIR}/lib/lib*.so*)
file(GLOB_RECURSE ALL_LIBS ${FASTDEPLOY_INSTALL_DIR}/third_libs/install/lib*.so*)
list(APPEND ALL_LIBS ${FASTDEPLOY_LIBS})
install(PROGRAMS ${ALL_LIBS} DESTINATION lib)

file(GLOB ADB_TOOLS run_with_adb.sh)
install(PROGRAMS ${ADB_TOOLS} DESTINATION ./)
