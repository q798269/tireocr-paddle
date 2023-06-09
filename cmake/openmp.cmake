# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if(ANDROID)
  if(NOT WITH_ANDROID_OPENMP)
    message(FATAL_ERROR "Please set WITH_ANDROID_OPENMP=ON before inclue openmp.cmake")
  endif()
  find_package(OpenMP REQUIRED)
  set(ENABLE_OPENMP_SHARED ON CACHE BOOL "" FORCE)
  if(WITH_ANDROID_LITE_STATIC)
    # Can use static/shared omp lib if WITH_LITE_STATIC=ON
    if(OPENMP_FOUND OR OpenMP_CXX_FOUND)
      add_definitions(-DWITH_ANDROID_OPENMP)
      if(${ANDROID_NDK_MAJOR})
        if(${ANDROID_NDK_MAJOR} GREATER 20)
          set(ENABLE_OPENMP_SHARED OFF CACHE BOOL "" FORCE)
          message(STATUS "ANDROID_NDK_MAJOR ${ANDROID_NDK_MAJOR} GREATER 20")
          set(OPENMP_LINK_FLAGS "-fopenmp -static-openmp")
        else()
          set(OPENMP_LINK_FLAGS "-fopenmp")
        endif()  
      endif()
    else()
      message(FATAL_ERROR "Could not found OpenMP!")  
    endif()
  else()
    if(OPENMP_FOUND OR OpenMP_CXX_FOUND)
      add_definitions(-DWITH_ANDROID_OPENMP)
      # Can only use shared omp lib if WITH_ANDROID_LITE_STATIC=OFF
      set(OPENMP_LINK_FLAGS "-fopenmp")
    else()
      message(FATAL_ERROR "Could not found OpenMP!")  
    endif()  
  endif()
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}" PARENT_SCOPE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}" PARENT_SCOPE)
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OPENMP_LINK_FLAGS}" PARENT_SCOPE)
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${OPENMP_LINK_FLAGS}" PARENT_SCOPE)
  message(STATUS "Found OpenMP ${OpenMP_VERSION} ${OpenMP_CXX_VERSION}")
  message(STATUS "OpenMP C flags:  ${OpenMP_C_FLAGS}")
  message(STATUS "OpenMP CXX flags:  ${OpenMP_CXX_FLAGS}")
  message(STATUS "OpenMP EXE LINKER flags:  ${OPENMP_LINK_FLAGS}")
  message(STATUS "OpenMP OpenMP_CXX_LIB_NAMES:  ${OpenMP_CXX_LIB_NAMES}")
  message(STATUS "OpenMP OpenMP_CXX_LIBRARIES:  ${OpenMP_CXX_LIBRARIES}")
  message(STATUS "ENABLE_OPENMP_SHARED: ${ENABLE_OPENMP_SHARED}")
else()
  message(FATAL_ERROR "WITH_ANDOIRD_OPENMP=ON option is not support for WIN32/APPLE/IOS/Linux!")
endif()
